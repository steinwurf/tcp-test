import argparse
import logging
import os
import asyncio
import pathlib

import detail.shell
import detail.ip
import detail.netns


def script_path():
    return pathlib.Path(__file__).resolve().parent


async def monitor():

    while True:
        await asyncio.sleep(1)

        tasks = asyncio.tasks.all_tasks()

        keep_running = False

        for t in tasks:
            try:
                if t.daemon == False:
                    keep_running = True
            except AttributeError:
                pass

        if not keep_running:
            for t in tasks:
                t.cancel()


async def network(log, result_path):

    shell = detail.shell.Shell(log=log, sudo=True)

    log.info("Creating namespaces")
    netns = detail.netns.NetNS(shell=shell, ip_factory=detail.ip.IP)
    namespaces = netns.list()

    if "demo0" in namespaces:
        netns.delete(name="demo0")

    if "demo1" in namespaces:
        netns.delete(name="demo1")

    demo0 = netns.add(name="demo0")
    demo1 = netns.add(name="demo1")

    ip = detail.ip.IP(shell=shell)
    ip.link_veth_add(p1_name="demo0-eth", p2_name="demo1-eth")
    ip.link_set(namespace="demo0", interface="demo0-eth")
    ip.link_set(namespace="demo1", interface="demo1-eth")

    demo0.addr_add(ip="10.0.0.1/24", interface="demo0-eth")
    demo1.addr_add(ip="10.0.0.2/24", interface="demo1-eth")

    demo0.up(interface="demo0-eth")
    demo1.up(interface="demo1-eth")

    demo0.up(interface="lo")
    demo1.up(interface="lo")

    demo0.tc(interface="demo0-eth", delay=20, loss=1)
    demo1.tc(interface="demo1-eth", delay=20, loss=1)

    log.debug(demo0.tc_show(interface="demo0-eth"))
    log.debug(demo1.tc_show(interface="demo1-eth"))

    try:
        # The location of the scripts

        await asyncio.gather(
            demo0.run_async("python3 server.py --packets 1000", cwd=script_path()),
            demo1.run_async(
                f"python3 client.py --server_ip 10.0.0.1 --clock-sync "
                f"--result_path={result_path.resolve()}",
                delay=2,
                cwd=script_path(),
            ),
            monitor(),
        )
    except asyncio.exceptions.CancelledError:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--packets", type=int, help="The number of packet to receive", default=10000
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Server port", default=False
    )

    parser.add_argument(
        "--packet_size", type=int, help="The number of packet to receive", default=1400
    )

    parser.add_argument(
        "--result_path", type=str, help="The path to the results", default="result.json"
    )

    log = logging.getLogger("client")
    log.addHandler(logging.StreamHandler())

    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    asyncio.run(network(log=log, result_path=pathlib.Path(args.result_path)))

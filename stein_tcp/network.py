import argparse
import subprocess
import logging
import os
import asyncio
import pathlib
import shutil
import time

from stein_tcp.util import shell, ip, netns, rely_tunnel



def script_path() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent


async def monitor(log: logging.Logger):

    while True:
        await asyncio.sleep(1)

        tasks: set[asyncio.Task] = asyncio.tasks.all_tasks()

        keep_running = False

        for t in tasks:
            try:
                if t.daemon == False:
                    keep_running = True
            except AttributeError:
                pass

        if not keep_running:
            log.debug("Cancelling tasks")
            for t in tasks:
                t.cancel()


async def network(
    log: logging.Logger,
    packets: int,
    packet_size: int,
    bandwidth: float | int,
    result_path: pathlib.Path | str | None,
    verbose: bool | None,
    rely_path: pathlib.Path | str | None,
    repair_interval: int,
    repair_target: int,
    timeout: int,
):

    server_ip = "10.0.0.1:12345"

    shell = shell.Shell(log=log, sudo=True)

    log.info("Creating namespaces")
    netns = netns.NetNS(shell=shell, ip_factory=ip.IP)
    namespaces = netns.list()

    if "demo0" in namespaces:
        netns.delete(name="demo0")

    if "demo1" in namespaces:
        netns.delete(name="demo1")

    demo0 = netns.add(name="demo0")
    demo1 = netns.add(name="demo1")

    ip = ip.IP(shell=shell)
    ip.link_veth_add(p1_name="demo0-eth", p2_name="demo1-eth")
    ip.link_set(namespace="demo0", interface="demo0-eth")
    ip.link_set(namespace="demo1", interface="demo1-eth")

    demo0.addr_add(ip=f"10.0.0.1/24", interface="demo0-eth")
    demo1.addr_add(ip=f"10.0.0.2/24", interface="demo1-eth")

    demo0.up(interface="demo0-eth")
    demo1.up(interface="demo1-eth")

    demo0.up(interface="lo")
    demo1.up(interface="lo")

    demo0.tc(interface="demo0-eth", delay=20, loss=1, jitter=10)
    demo1.tc(interface="demo1-eth", delay=20, loss=1, jitter=10)

    log.debug(demo0.tc_show(interface="demo0-eth"))
    log.debug(demo1.tc_show(interface="demo1-eth"))

    if rely_path:

        log.debug("Starting Rely Daemon Servers...")

        rely_tunnel0 = rely_tunnel.RelyTunnel(
            shell=demo0.shell,
            rely_path=rely_path,
        )
        rely_tunnel1 = rely_tunnel.RelyTunnel(
            shell=demo1.shell,
            rely_path=rely_path,
        )

        rely_tunnel0.init()
        rely_tunnel1.init()

        log.debug("Servers init'ed")

        time.sleep(2)

        log.debug("Adding and starting tunnels")

        rely_tunnel0.start_tunnel(
            id="demo0tun",
            tunnel_ip="11.11.11.11",
            tunnel_in=f"{server_ip}",
            tunnel_out=f"10.0.0.2:12345",
            packet_size=packet_size,
        )

        rely_tunnel1.start_tunnel(
            id="demo1tun",
            tunnel_ip="11.11.11.22",
            tunnel_in=f"10.0.0.2:12345",
            tunnel_out=f"{server_ip}",
            packet_size=packet_size,
        )

        log.debug(
            f"Setting Repair Interval = {repair_interval}, Repair Target = {repair_target}"
        )

        rely_tunnel0.set_repair(
            id="demo0tun",
            repair_interval=repair_interval,
            repair_target=repair_target,
        )

        rely_tunnel1.set_repair(
            id="demo1tun",
            repair_interval=repair_interval,
            repair_target=repair_target,
        )

        log.debug(f"Setting Encoder/Decoder timeout = {timeout}")

        rely_tunnel0.set_encoder_timeout(id="demo0tun", timeout=timeout)

        rely_tunnel1.set_encoder_timeout(id="demo1tun", timeout=timeout)

        rely_tunnel0.set_decoder_timeout(id="demo0tun", timeout=timeout)

        rely_tunnel1.set_decoder_timeout(id="demo1tun", timeout=timeout)

        server_ip = "11.11.11.11:12345"

    try:
        # The location of the scripts

        await asyncio.gather(
            demo0.run_async(
                f"python3 server.py --packets {packets} --packet_size {packet_size} --server_ip {server_ip} --bandwidth {bandwidth}",
                delay=2,
                cwd=script_path(),
            ),
            demo1.run_async(
                f"python3 client.py --server_ip {server_ip} --packet_size {packet_size} --clock-sync "
                f"--result_path={result_path.resolve()} {verbose}",
                delay=4,
                cwd=script_path(),
            ),
            monitor(log=log),
        )

    except asyncio.exceptions.CancelledError:
        pass


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--packets",
        type=int,
        help="The number of packet to receive",
        default=1000,
    )

    parser.add_argument(
        "-b",
        "--bandwidth",
        type=float,
        help="The bandwidth from the server to the client in MB/s",
        default=1,
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Get debug info", default=False
    )

    parser.add_argument(
        "-l",
        "--packet_size",
        type=int,
        help="The number of packet to receive",
        default=1300,
    )

    parser.add_argument(
        "-o",
        "--result_path",
        type=str,
        help="The path to the results",
        default="result.json",
    )

    parser.add_argument(
        "-p",
        "--rely_path",
        type=str,
        help="The path to the rely_app binary",
        default="rely",
    )

    parser.add_argument(
        "-k",
        "--repair_interval",
        type=int,
        help="The distance in packets between each generation of repair",
        default=5,
    )
    parser.add_argument(
        "-r",
        "--repair_target",
        type=int,
        help="The number of repair packets to generate at each generation",
        default=1,
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        help="The time a packet is held by the encoder/decoder",
        default=60,
    )

    log = logging.getLogger("client")
    log.addHandler(logging.StreamHandler())

    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)
        verbose = "--verbose"
    else:
        log.setLevel(logging.INFO)
        verbose = ""

    shell = shell.Shell(log=log, sudo=False)

    rely_path = None

    if args.rely_path == "rely":
        try:
            shell.run("rely -v")
            rely_path = "rely"
        except subprocess.CalledProcessError:
            try:
                shell.run("rely_app -v")
                rely_path = "rely_app"
            except subprocess.CalledProcessError:
                rely_path = shutil.which("rely") or shutil.which("rely_app")

    asyncio.run(
        network(
            log=log,
            packets=args.packets,
            packet_size=args.packet_size,
            bandwidth=args.bandwidth,
            result_path=pathlib.Path(args.result_path),
            verbose=verbose,
            rely_path=rely_path,
            repair_interval=args.repair_interval,
            repair_target=args.repair_target,
            timeout=args.timeout,
        )
    )


if __name__ == "__main__":
    main()

import argparse
import logging
import os
import asyncio
import pathlib
import time

import detail.shell
import detail.ip
import detail.netns
import detail.rely_tunnel
import detail.iperf_shell


def script_path():
    return pathlib.Path(__file__).resolve().parent


async def monitor(log):

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
            log.debug("Cancelling tasks")
            for t in tasks:
                t.cancel()


async def iperf(
    log,
    packets,
    packet_size,
    throughput,
    result_path,
    rely_path,
    repair_interval,
    repair_target,
    timeout,
):

    server_port = 12345
    server_ip = "10.0.0.1"

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

    iperf_server = detail.iperf_shell.iPerfShell(shell=demo0.shell)
    iperf_client = detail.iperf_shell.iPerfShell(shell=demo1.shell)

    ip = detail.ip.IP(shell=shell)
    ip.link_veth_add(p1_name="demo0-eth", p2_name="demo1-eth")
    ip.link_set(namespace="demo0", interface="demo0-eth")
    ip.link_set(namespace="demo1", interface="demo1-eth")

    demo0.addr_add(ip=f"10.0.0.1/24", interface="demo0-eth")
    demo1.addr_add(ip=f"10.0.0.2/24", interface="demo1-eth")

    demo0.up(interface="demo0-eth")
    demo1.up(interface="demo1-eth")

    demo0.up(interface="lo")
    demo1.up(interface="lo")

    demo0.tc(interface="demo0-eth", delay=1000, loss=1, limit=15000)
    demo1.tc(interface="demo1-eth", delay=1000, loss=1, limit=15000)

    log.debug(demo0.tc_show(interface="demo0-eth"))
    log.debug(demo1.tc_show(interface="demo1-eth"))

    if rely_path:

        log.debug("Starting Rely Daemon Servers...")

        rely_tunnel0 = detail.rely_tunnel.RelyTunnel(
            shell=demo0.shell,
            rely_path=rely_path,
        )
        rely_tunnel1 = detail.rely_tunnel.RelyTunnel(
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
            tunnel_in=f"{server_ip}:12345",
            tunnel_out=f"10.0.0.2:12345",
            packet_size=packet_size,
        )

        rely_tunnel1.start_tunnel(
            id="demo1tun",
            tunnel_ip="11.11.11.22",
            tunnel_in=f"10.0.0.2:12345",
            tunnel_out=f"{server_ip}:12345",
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

        server_ip = "11.11.11.11"

    try:
        # The location of the scripts

        await asyncio.gather(
            iperf_server.run_async(
                f"--server --json --logfile {result_path} --interval 1",
                delay=2,
                cwd=script_path(),
                daemon=True,
            ),
            iperf_client.run_async(
                f"--client {server_ip} --bandwidth {throughput} --blockcount {packets} --length {packet_size} --no-delay",
                delay=4,
                cwd=script_path(),
            ),
            monitor(log=log),
        )

    except asyncio.exceptions.CancelledError:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--packets", type=int, help="The number of packet to receive", default=1000
    )

    parser.add_argument(
        "--throughput",
        type=float,
        help="The throughput from the server to the client in bits/s",
        default=10000000,
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Get debug info", default=False
    )

    parser.add_argument(
        "--packet_size", type=int, help="The size of the packets to send", default=1300
    )

    parser.add_argument(
        "--result_path", type=str, help="The path to the results", default="result.json"
    )

    parser.add_argument(
        "--rely_path",
        type=str,
        help="The path to the rely_app binary",
        default=None,
    )

    parser.add_argument(
        "--repair_interval",
        type=int,
        help="The distance in packets between each generation of repair",
        default=4,
    )
    parser.add_argument(
        "--repair_target",
        type=int,
        help="The number of repair packets to generate at each generation",
        default=1,
    )

    parser.add_argument(
        "--timeout",
        type=int,
        help="The time a packet is held by the encoder/decoder",
        default=20,
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

    if args.rely_path:
        rely_path = pathlib.Path(args.rely_path).resolve()

    else:
        rely_path = None

    asyncio.run(
        iperf(
            log=log,
            packets=args.packets,
            packet_size=args.packet_size,
            throughput=args.throughput,
            result_path=pathlib.Path(args.result_path),
            rely_path=rely_path,
            repair_interval=args.repair_interval,
            repair_target=args.repair_target,
            timeout=args.timeout,
        )
    )

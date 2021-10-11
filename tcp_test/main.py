import argparse
import asyncio
import logging
import pathlib
import time

from tcp_test import __version__
from . import network
from . import iperf
from . import server
from . import client
from . import plot


def main(command_line=None):
    parser = argparse.ArgumentParser("tcp-test")
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + __version__
    )

    subparsers = parser.add_subparsers(dest="command")

    network = subparsers.add_parser("network", help="Run a network namespace test")

    iperf = subparsers.add_parser("iperf", help="Run an iPerf TCP test")

    client = subparsers.add_parser("client", help="Run a standalone TCP client")

    server = subparsers.add_parser("server", help="Run a standalone TCP server")

    plot = subparsers.add_parser(
        "plot", help="Generate plots from results in JSON-format"
    )

    args = parser.parse_args(command_line)
    if args.command == "network":
        network_run(parser=network)

    elif args.command == "iperf":
        iperf_run(parser=iperf)

    elif args.command == "client":
        client_run(parser=client)

    elif args.command == "server":
        server_run(parser=server)

    elif args.command == "plot":
        plot_run(parser=plot)

    else:
        raise RuntimeError("Wrong subcommand was passed")


def network_run(parser: argparse.ArgumentParser):

    log = logging.getLogger("client")
    log.addHandler(logging.StreamHandler())

    parser = network.setup_network_arguments(parser=parser)

    args = parser.parse_known_args()[0]

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
        network.network(
            log=log,
            packets=args.packets,
            packet_size=args.packet_size,
            throughput=args.throughput,
            result_path=pathlib.Path(args.result_path),
            verbose=verbose,
            rely_path=rely_path,
            repair_interval=args.repair_interval,
            repair_target=args.repair_target,
            timeout=args.timeout,
        )
    )


def iperf_run(parser: argparse.ArgumentParser):

    log = logging.getLogger("client")
    log.addHandler(logging.StreamHandler())

    parser = iperf.setup_iperf_arguments(parser=parser)

    args = parser.parse_known_args()[0]

    if args.verbose:
        log.setLevel(logging.DEBUG)

    else:
        log.setLevel(logging.INFO)

    if args.rely_path:
        rely_path = pathlib.Path(args.rely_path).resolve()

    else:
        rely_path = None

    asyncio.run(
        iperf.iperf(
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


def client_run(parser: argparse.ArgumentParser):

    log = logging.getLogger("client")
    log.addHandler(logging.StreamHandler())

    parser = client.setup_client_arguments(parser=parser)

    args = parser.parse_known_args()[0]

    if args.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    statistics_collector = client.setup_statistics(clock_sync=args.clock_sync, log=log)

    start_time = time.time()

    client.client(
        server_port=args.server_port,
        server_ip=args.server_ip,
        packet_size=args.packet_size,
        statistics_collector=statistics_collector,
        result_path=pathlib.Path(args.result_path),
        log=log,
    )

    elapsed_time = time.time() - start_time

    log.info(f"Time Elapsed: {elapsed_time} s")
    log.info(
        f"Packets Received: {statistics_collector.collectors[0].statistics.packets_received}"
    )


def server_run(parser: argparse.ArgumentParser):

    log = logging.getLogger("server")
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.INFO)

    parser = server.setup_server_arguments(parser=parser)

    args = parser.parse_known_args()[0]

    server.server(
        packets=args.packets,
        throughput=args.throughput,
        packet_size=args.packet_size,
        server_ip=args.server_ip,
        server_port=args.server_port,
        log=log,
    )


def plot_run(parser: argparse.ArgumentParser):

    log = logging.getLogger("client")
    log.addHandler(logging.StreamHandler())

    parser = plot.setup_plot_arguments(parser=parser)

    args = parser.parse_known_args()[0]

    if args.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    json_path = pathlib.Path(args.json_path).resolve()
    plot_path = pathlib.Path(args.plot_path).resolve()

    plot.plot(
        log=log,
        json_path=json_path,
        plot_path=plot_path,
        rely=args.rely,
        rtt=args.rtt,
        loss=args.loss,
        capacity=args.capacity,
    )

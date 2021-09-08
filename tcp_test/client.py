import socket
import struct
import time
import argparse
import logging
from console_statistics import ConsoleStatistics
from regular_statistics import PacketStatistics, JitterStatistics, LatencyStatistics
from statistics_collector import StatisticsCollector


def client(server_ip, server_port, packet_size, statistics_collector, log):

    client = socket.socket()
    client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    server_address = (server_ip, server_port)
    log.info(f"Connecting to (Server, Port): {server_address}")

    client.connect(server_address)
    client.sendall(bytearray("Hello, Server", "utf-8"))

    log.info("Running")

    while True:

        # We run until the server disconnects

        try:
            data = client.recv(packet_size, socket.MSG_WAITALL)
        except Exception as e:
            log.error(f"{e}")
            break

        if len(data) != packet_size:
            log.debug(f"Got wrong sized packet {len(data)}")
            break

        log.debug(f"Got from server {len(data)} bytes")

        server_time = struct.unpack_from("<Q", data, 0)[0]
        client_time = int(time.time_ns() / 1000000)

        statistics_collector.add_result(
            server_time=server_time, client_time=client_time, bytes_received=len(data)
        )
        statistics_collector.report()

    client.close()
    log.info("Client stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--server_ip",
        type=str,
        help="Server IP address",
        default="127.0.0.1",
    )

    parser.add_argument(
        "--server_port",
        type=int,
        help="Server port",
        default=12345,
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Server port", default=False
    )

    parser.add_argument(
        "--packet_size", type=int, help="The number of packet to receive", default=1400
    )

    parser.add_argument(
        "--clock-sync",
        action="store_true",
        help="If the server and client clocks are synchronized",
        default=False,
    )

    log = logging.getLogger("client")
    log.addHandler(logging.StreamHandler())

    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    report_interval = 100

    packet_statistics = PacketStatistics(log=log)
    packet_console = ConsoleStatistics(log=log, statistics=packet_statistics)

    jitter_statistics = JitterStatistics(log=log)
    jitter_console = ConsoleStatistics(log=log, statistics=jitter_statistics)

    collectors = [packet_console, jitter_console]

    if args.clock_sync:

        latency_statistics = LatencyStatistics(log=log)
        latency_console = ConsoleStatistics(log=log, statistics=latency_statistics)
        collectors.append(latency_console)

    statistics_collector = StatisticsCollector(
        collectors=collectors, report_interval=report_interval
    )

    start_time = time.time()

    client(
        server_port=args.server_port,
        server_ip=args.server_ip,
        packet_size=args.packet_size,
        statistics_collector=statistics_collector,
        log=log,
    )

    elapsed_time = time.time() - start_time

    log.info(f"Time Elapsed: {elapsed_time} s")
    log.info(f"Packets Received: {packet_statistics.packets_received}")

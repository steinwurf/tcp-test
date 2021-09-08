import socket
import struct
import time
import atexit
import json
import os
import argparse
import logging


def client(server_ip, server_port, packet_size, statistics, log):

    client = socket.socket()
    client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    server_address = (server_ip, server_port)
    log.info(f"Connecting to (Server, Port): {server_address}")

    client.connect(server_address)
    client.sendall(bytearray("Hello, Server", "utf-8"))

    log.info("Running")

    statistics.start()

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

        statistics.add_result(server_time=server_time,
                              client_time=client_time, bytes_received=len(data))

    statistics.stop()

    client.close()
    log.info("Client stopped")


class ConsoleStatistics:

    def __init__(self, log):
        self.server_time = []
        self.client_time = []
        self.bytes_received = 0
        self.packet_received = 0

        self.log = log
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.log.info(f"Test elapsed: {time.time() - self.start_time} s")
        self.log.info(f"Packets collected: {self.packet_received}")

    def add_result(self, server_time, client_time, bytes_received):

        self.log.debug(f"Added result")

        self.server_time.append(server_time)
        self.client_time.append(client_time)
        self.bytes_received += bytes_received
        self.packet_received += 1


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
        "--verbose",
        action="store_true",
        help="Server port",
        default=False)

    parser.add_argument(
        "--packet_size", type=int, help="The number of packet to receive",
        default=1400
    )

    log = logging.getLogger('client')
    log.addHandler(logging.StreamHandler())

    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    statistics = ConsoleStatistics(log=log)

    client(server_port=args.server_port, server_ip=args.server_ip,
           packet_size=args.packet_size, statistics=statistics, log=log)

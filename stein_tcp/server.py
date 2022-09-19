import socket
import struct
import time
import argparse
import logging

__all__ = ["server", "server_cli"]


def calculate_interval(
    buffer_size: int,
    bandwidth: float or int,
) -> float:
    bandwidth = bandwidth * 1024 * 1024
    return buffer_size / bandwidth


def run(
    client_socket: socket.socket,
    packets: int,
    packet_size: int,
    interval: int,
    log: logging.Logger,
):

    packets_sent = 0

    while packets_sent < packets:
        data = bytearray(packet_size)
        server_time = int(time.time_ns() / 1000000)

        log.debug(f"Server Time: {server_time}")

        struct.pack_into("<Q", data, 0, server_time)

        try:
            client_socket.sendall(data)
        except Exception as e:
            log.error(e)
            break

        packets_sent += 1

        time.sleep(interval)

    client_socket.close()


def server(
    packets: int,
    bandwidth: int | float,
    server_ip: str,
    packet_size: int,
    log: logging.Logger,
):

    sock = socket.socket()
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = server_ip.split(":")
    server_address = (server_address[0], int(server_address[1]))

    log.info(f"Starting up (Server, Port): {server_address}")
    sock.bind(server_address)

    sock.listen(1)
    interval = calculate_interval(packet_size, bandwidth)

    log.info("Waiting for Client to connect...")
    client_socket, client_address = sock.accept()
    log.info(f"Connection from {client_address}")

    # Receive hello from client
    data = client_socket.recv(packet_size).decode()
    log.info(f"Got from client {data}")

    try:
        log.info("Running")

        run(
            client_socket=client_socket,
            packets=packets,
            packet_size=packet_size,
            interval=interval,
            log=log,
        )

    finally:

        sock.close()
        log.info("Server stopped")


def server_cli():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-i",
        "--packets",
        type=int,
        help="The number of packet to receive",
        default=1000,
        metavar="",
    )

    parser.add_argument(
        "-l",
        "--packet_size",
        type=int,
        help="The number of packet to receive",
        default=1400,
        metavar="",
    )

    parser.add_argument(
        "-s",
        "--server_ip",
        type=str,
        help="The IP address the server listens for connections to",
        default="0.0.0.0:12345",
        metavar="",
    )

    parser.add_argument(
        "-b",
        "--bandwidth",
        type=float,
        help="The bandwidth from the server to the client in MB/s",
        default=1,
        metavar="",
    )

    log = logging.getLogger("server")
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.INFO)

    args = parser.parse_args()

    server(
        packets=args.packets,
        bandwidth=args.bandwidth,
        packet_size=args.packet_size,
        server_ip=args.server_ip,
        log=log,
    )


if __name__ == "__main__":
    server_cli()

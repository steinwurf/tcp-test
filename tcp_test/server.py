import socket
import struct
import time
import argparse
import logging


def calculate_interval(buffer_size: int, throughput: float or int):
    throughput = throughput * 1024 * 1024
    return buffer_size / throughput


def run(client_socket, packets, packet_size, interval, log):

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


def server(packets, throughput, server_ip, server_port, packet_size, log):

    sock = socket.socket()
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = (server_ip, server_port)

    log.info(f"Starting up (Server, Port): {server_address}")
    sock.bind(server_address)

    sock.listen(1)
    interval = calculate_interval(packet_size, throughput)

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--packets", type=int, help="The number of packet to receive", default=10000
    )

    parser.add_argument(
        "--packet_size", type=int, help="The number of packet to receive", default=1400
    )

    parser.add_argument(
        "--throughput",
        type=float,
        help="The throughput from the server to the client in MB/s",
        default=1,
    )

    log = logging.getLogger("server")
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.INFO)

    server_ip = "0.0.0.0"
    server_port = 12345

    args = parser.parse_args()

    server(
        packets=args.packets,
        throughput=args.throughput,
        packet_size=args.packet_size,
        server_ip=server_ip,
        server_port=server_port,
        log=log,
    )

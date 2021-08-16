import os
import socket
import timeit
import struct
import sys
import time
import atexit
import argparse


def calculate_interval(buffer_size: int, throughput: float or int):
    throughput = throughput * 1024 * 1024
    return buffer_size/throughput


def server():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--tries',
        type=int,
        help='The number of packets to send',
        default=10000
    )
    parser.add_argument(
        '--throughput',
        type=float,
        help='The wanted throughput from the server side in MB/s',
        default=1
    )
    parser.add_argument(
        '--rely',
        type=str,
        help='A bool determining if rely is activated or not',
        default="False"
    )
    args = parser.parse_args()
    args.rely = (args.rely == 'true')
    if args.rely:
        TCP_IP = '11.11.11.11'
        client_ip = '11.11.11.22'
    else:
        TCP_IP = '10.0.0.1'
        client_ip = '10.0.0.2'
    TCP_PORT = 5000
    BUFFERSIZE = 1400
    sock = socket.socket()

    server_address = (TCP_IP, TCP_PORT)

    print(f"Starting up (Server, Port): {server_address}")
    sock.bind(server_address)

    sock.listen(1)
    interval = calculate_interval(BUFFERSIZE, args.throughput)

    print("Waiting for Client to connect...")
    client_socket, client_address = sock.accept()
    print(f"Connection from {client_address}")
    packets_sent = 0
    while True:
        data = client_socket.recv(BUFFERSIZE).decode()
        print(data)
        if not data:
            break
        while packets_sent < args.tries:
            data = bytearray(BUFFERSIZE)
            server_time = int(time.time_ns()/1000000)
            print(f"Server Time: {server_time}")
            struct.pack_into("<Q", data, 0, server_time)
            client_socket.sendall(data)
            packets_sent += 1
            time.sleep(interval)

    data = client_socket.recv(BUFFERSIZE).decode()
    print(data)
    sock.close()


if __name__ == "__main__":
    server()

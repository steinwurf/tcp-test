import socket
import struct
import time
import atexit
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpl_patches
from matplotlib.legend import Legend
import argparse


def throughput_filename(files: int, throughput: float, rely_on: bool):
    if rely_on:
        return f"./results/rely/rely_throughput{throughput}_file{files}.json"
    else:
        return f"./results/tcp/throughput{throughput}_file{files}.json"


def throughput_files(throughput: float, rely_on: bool):
    files = 0
    while os.path.exists(throughput_filename(files, throughput, rely_on)):
        files += 1
    return files


def latencies(
    latency_dict: dict,
    packets: int,
    server_latency: int,
    client_latency: int,
    packet_loss: int,
    throughput: int,
    rely_on: bool,
):
    df = pd.DataFrame(latency_dict)
    print(df)
    plt.hist(x="Added Latency / ms", bins=100, data=df)
    plt.xlabel("Added Latency / ms")
    plt.ylabel("Count")
    handles = [
        mpl_patches.Rectangle((0, 10), 1, 1, fc="white", ec="white", lw=0, alpha=0)
    ] * 6

    labels = []
    labels.append(f"Rely = {rely_on}")
    if rely_on:
        labels.append("Repair rate = 16.6%")
    labels.append(f"Packets = {packets}")
    labels.append(f"Throughput = {throughput} MB/s")
    labels.append(f"Packet Loss = {packet_loss}%")
    labels.append(f"S->C delay = {server_latency}ms")
    labels.append(f"C->S delay = {client_latency}ms")
    plt.legend(
        handles,
        labels,
        loc=0,
        fontsize="small",
        fancybox=True,
        framealpha=0.7,
        handlelength=0,
        handletextpad=0,
    )
    plt.title(f"TCP Test\n")
    plt.show()


def test_throughput(
    stats: dict,
    start_time: float,
    packets: int,
    server_latency: int,
    client_latency: int,
    packet_loss: int,
    throughput: int,
    rely: bool,
):
    time_elapsed = time.time() - start_time
    results = {
        "Mean Throughput / MB/s": stats["byte_count"] / (time_elapsed * 1024 * 1024),
        "Packet Loss %": packet_loss,
        "Server Latency": server_latency,
        "Client Latency": client_latency,
        "Server Throughput": throughput,
        "With Rely": rely,
        "Transfers": packets,
    }
    print(results)
    current_throughput_files = throughput_files(throughput=throughput, rely_on=rely)
    if rely:
        json.dump(
            results,
            open(
                f"./results/rely/rely_throughput{throughput}_file{current_throughput_files}.json",
                "w",
            ),
        )
    else:
        json.dump(
            results,
            open(
                f"./results/tcp/throughput{throughput}_file{current_throughput_files}.json",
                "w",
            ),
        )


def client(mode, packets, server_latency, client_latency, loss, throughput, rely):

    latency = {"Added Latency / ms": []}
    if rely:
        server_ip = "11.11.11.11"
    else:
        server_ip = "10.0.0.1"
    server_port = 5000
    BUFFERSIZE = 100
    if mode == "histogram":
        atexit.register(
            latencies,
            latency,
            packets,
            server_latency,
            client_latency,
            loss,
            throughput,
            rely,
        )

    client = socket.socket()

    server_address = (server_ip, server_port)
    print(f"Connecting to (Server, Port): {server_address}")

    client.connect(server_address)
    client.sendall(bytearray("Hello, Server", "utf-8"))

    stats = {"byte_count": 0}
    if mode == "throughput":
        start_time = time.time()
        atexit.register(
            test_throughput,
            stats,
            start_time,
            packets,
            server_latency,
            client_latency,
            loss,
            throughput,
            rely,
        )
    packets_received = 0
    while packets_received < packets:
        data = client.recv(BUFFERSIZE, socket.MSG_WAITALL)
        stats["byte_count"] += BUFFERSIZE

        (server_time,) = struct.unpack_from("<Q", data, 0)
        client_time = int(time.time_ns() / 1000000)
        elapsed_time = client_time - server_time

        print(f"Packet No.: {packets_received}, Time elapsed: {elapsed_time} ms")
        latency["Added Latency / ms"].append(elapsed_time - server_latency)
        packets_received += 1
    client.sendall(bytearray("Received All", "utf-8"))
    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        type=str,
        help="The mode for data collection. histogram or throughput",
        default="histogram",
    )
    parser.add_argument(
        "--packets", type=int, help="The number of packet to receive", default=10000
    )
    parser.add_argument(
        "--server-latency",
        type=int,
        help="The delay from the server to the client in ms",
        default=60,
    )
    parser.add_argument(
        "--client-latency",
        type=int,
        help="The delay from the client to the server in ms",
        default=60,
    )
    parser.add_argument(
        "--packet-loss", type=float, help="The packet loss used", default=0
    )
    parser.add_argument(
        "--throughput",
        type=float,
        help="The throughput from the server to the client in MB/s",
        default=1,
    )
    parser.add_argument(
        "--rely",
        type=str,
        help="A bool determining if rely is activated or not",
        default="False",
    )

    args = parser.parse_args()
    args.rely = args.rely == "true"

    client(
        args.mode,
        args.packets,
        args.server_latency,
        args.client_latency,
        args.packet_loss,
        args.throughput,
        args.rely,
    )

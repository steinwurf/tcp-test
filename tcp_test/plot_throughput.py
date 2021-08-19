import json
import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from os import path


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--throughput",
        type=float,
        help="the specific throughput in the test.",
        default=1,
    )
    args = parser.parse_args()
    results = {
        "Average Throughput / MB/s": [],
        "Packet Loss / %": [],
        "Rely": [],
        "Server Latency": [],
        "Client Latency": [],
        "Server Throughput": [],
        "Transfers": [],
    }
    files = 0
    while path.exists(f"./results/tcp/throughput{args.throughput}_file{files}.json"):
        files += 1
    for i in range(files):
        with open(f"./results/tcp/throughput{args.throughput}_file{i}.json", "r") as f:
            temp = json.load(f)
            print(temp)
            results["Average Throughput / MB/s"].append(temp["Mean Throughput / MB/s"])
            results["Packet Loss / %"].append(temp["Packet Loss %"])
            results["Rely"].append("OFF")
            results["Server Latency"].append(temp["Server Latency"])
            results["Client Latency"].append(temp["Client Latency"])
            results["Server Throughput"].append(temp["Server Throughput"])
            results["Transfers"].append(temp["Transfers"])
    rely_files = 0
    while path.exists(
        f"./results/rely/rely_throughput{args.throughput}_file{rely_files}.json"
    ):
        rely_files += 1
    for i in range(rely_files):
        with open(
            f"./results/rely/rely_throughput{args.throughput}_file{i}.json", "r"
        ) as f:
            temp = json.load(f)
            print(temp)
            results["Average Throughput / MB/s"].append(temp["Mean Throughput / MB/s"])
            results["Packet Loss / %"].append(temp["Packet Loss %"])
            results["Rely"].append("ON, (5,1)")
            results["Server Latency"].append(temp["Server Latency"])
            results["Client Latency"].append(temp["Client Latency"])
            results["Server Throughput"].append(temp["Server Throughput"])
            results["Transfers"].append(temp["Transfers"])
    df = pd.DataFrame(results)
    print(df)
    df["Simulation"] = "Rely: " + df["Rely"].astype(str)
    sns.lineplot(
        x="Packet Loss / %",
        y="Average Throughput / MB/s",
        hue="Simulation",
        data=df,
        estimator=np.mean,
    )
    plt.title(
        "TCP throughput \n"
        + f'Packets = {temp["Transfers"]}\n'
        + (
            f'Server Throughput = {temp["Server Throughput"]} MB/s\n'
            + (
                f'S->C = {temp["Server Latency"]}ms\n'
                + (f'C->S = {temp["Client Latency"]}ms\n')
            )
        )
    )
    plt.show()


if __name__ == "__main__":
    main()

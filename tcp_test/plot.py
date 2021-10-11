import pandas
import matplotlib.pyplot as plt
import argparse
import logging
import pathlib
import json


def plot(log, json_path, plot_path, rely, rtt, loss, capacity):

    log.info(f"Gathering results from {json_path}")

    log.debug("Opening file")
    with open(json_path, "r") as f:
        log.debug("Loading json")
        results = json.loads(f.read())

    if "start" in results.keys():

        log.info(f"Plotting iperf3 results")
        fixed_keys = ["end", "bits_per_second"]

        target_bitrate = round(results["start"]["target_bitrate"] / (1000 * 1000))

        results = results["intervals"]

        intervals = []
        bitrates = []

        for dict in results[:-1]:
            if dict["streams"][0]["omitted"]:
                continue
            intervals.append(round(dict["streams"][0]["start"]))
            bitrates.append(dict["streams"][0]["bits_per_second"] / (1000 * 1000))

        results = {"time": intervals, "mbitrate": bitrates}

        df = pandas.DataFrame(results)

        if rely:
            label = "Rely"
            color = "-r"
        else:
            label = "TCP"
            color = "-b"

        if rtt:
            label += f"\nRTT = {rtt}ms"
        if loss:
            label += f"\nLoss = {round(loss, 2)}%"
        if capacity:
            label += f"\nLink-capacity = {round(capacity,2)}Mbit"

        log.debug("Throughput Line")
        plt.plot(
            df["time"],
            df["mbitrate"],
            color,
            linewidth=1,
            label=label,
        )
        plt.legend()
        plt.ylabel("Throughput / Mbit/s")
        plt.xlabel("Time / s")
        plt.title(f"Throughput over time\nTarget Throughput = {target_bitrate} Mbit/s")
        plt.grid(True)

        plt.savefig(plot_path / "throughput_line.png")
        plt.savefig(plot_path / "throughput_line.svg")

        plt.close()

    else:

        total_packets = results["packets_received"]

        del results["bytes_received"]
        del results["packets_received"]

        results["packet_index"] = [i for i in range(total_packets)]

        df = pandas.DataFrame(results)

        log.info("Jitter: Plotting..")

        log.debug("Jitter Histogram")

        label = ""

        if rely:
            label = "Rely"
        else:
            label = "TCP"

        plt.hist(
            df["jitter"],
            bins=100,
            label=label,
        )
        plt.legend(loc="upper right")
        plt.xlabel("Jitter / ms")
        plt.ylabel("Count")
        plt.title("Jitter Histogram")
        plt.grid(True)

        plt.savefig(plot_path / "jitter_hist.png")
        plt.savefig(plot_path / "jitter_hist.svg")

        plt.close()

        log.debug("Jitter Scatter")
        plt.scatter(
            df["packet_index"],
            df["jitter"],
            s=10,
            label=label,
        )
        plt.legend(loc="upper right")
        plt.ylabel("Jitter / ms")
        plt.xlabel("Packet Index")
        plt.title("Jitter vs Packet Index")
        plt.grid(True)

        plt.savefig(plot_path / "jitter_scatter.png")
        plt.savefig(plot_path / "jitter_scatter.svg")

        plt.close()

        log.debug("Jitter Line")
        plt.plot(
            df["packet_index"],
            df["jitter"],
            linewidth=1,
            label=label,
        )
        plt.legend(loc="upper right")
        plt.ylabel("Jitter / ms")
        plt.xlabel("Packet Index")
        plt.title("Jitter vs Packet Index")
        plt.grid(True)

        plt.savefig(plot_path / "jitter_line.png")
        plt.savefig(plot_path / "jitter_line.svg")

        plt.close()

        log.info("Jitter: Done!")

        if "latency" in results.keys():

            log.info("Latency: Plotting..")

            log.debug("Latency Histogram")

            plt.hist(
                df["latency"],
                bins=100,
                label=label,
            )
            plt.legend(loc="upper right")
            plt.xlabel("Latency / ms")
            plt.ylabel("Count")
            plt.title("Latency Histogram")
            plt.grid(True)

            plt.savefig(plot_path / "latency_hist.png")
            plt.savefig(plot_path / "latency_hist.svg")

            plt.close()

            log.debug("Latency Scatter")

            plt.scatter(
                df["packet_index"],
                df["latency"],
                s=10,
                label=label,
            )
            plt.legend(loc="upper right")
            plt.ylabel("Latency / ms")
            plt.xlabel("Packet Index")
            plt.title("Latency vs Packet Index")
            plt.grid(True)

            plt.savefig(plot_path / "latency_scatter.png")
            plt.savefig(plot_path / "latency_scatter.svg")

            plt.close()

            log.debug("Latency Line")

            plt.plot(
                df["packet_index"],
                df["latency"],
                linewidth=1,
                label=label,
            )
            plt.legend(loc="upper right")
            plt.ylabel("Latency / ms")
            plt.xlabel("Packet Index")
            plt.title("Latency vs Packet Index")
            plt.grid(True)

            plt.savefig(plot_path / "latency_line.png")
            plt.savefig(plot_path / "latency_line.svg")

            plt.close()

            log.info("Latency: Done!")

        log.info(f"All Done. Plots are saved in: {plot_path}")


def setup_plot_arguments(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:

    parser.add_argument(
        "--json_path",
        type=str,
        help="The path to the json results",
        default="result.json",
    )

    parser.add_argument(
        "--plot_path",
        type=str,
        help="The path to the directory where the plots will be stored",
        default="./",
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Get debug information", default=False
    )

    parser.add_argument(
        "--rely",
        action="store_true",
        help="If the results are with rely or not",
        default=False,
    )

    parser.add_argument(
        "--rtt",
        type=int,
        help="RTT of results in ms. For the legend",
        default=None,
    )

    parser.add_argument(
        "--loss",
        type=float,
        help="Packet loss percentage of results. For the legend",
        default=None,
    )

    parser.add_argument(
        "--capacity",
        type=float,
        help="The Link capacity of results. For the legend",
        default=None,
    )

    return parser


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    log = logging.getLogger("client")
    log.addHandler(logging.StreamHandler())

    parser = setup_plot_arguments(parser=parser)

    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    json_path = pathlib.Path(args.json_path).resolve()
    plot_path = pathlib.Path(args.plot_path).resolve()

    plot(
        log=log,
        json_path=json_path,
        plot_path=plot_path,
        rely=args.rely,
        rtt=args.rtt,
        loss=args.loss,
        capacity=args.capacity,
    )

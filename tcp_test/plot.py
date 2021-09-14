import pandas
import argparse
import logging
import pathlib
import json


def plot(log, json_path, plot_path):

    log.info(f"Gathering results from {json_path}")

    log.debug("Opening file")
    with open(json_path, "r") as f:
        log.debug("Loading json")
        results = json.loads(f.read())

    total_packets = results["packets_received"]

    del results["bytes_received"]
    del results["packets_received"]

    results["packet_index"] = [i for i in range(total_packets)]

    df = pandas.DataFrame(results)

    log.info("Jitter: Plotting..")

    log.debug("Jitter Histogram")

    jitter_hist = df.plot(
        y="jitter", xlabel="Jitter / ms", ylabel="Count", kind="hist", grid=True
    ).get_figure()
    jitter_hist.savefig(plot_path / "jitter_hist.png")
    jitter_hist.savefig(plot_path / "jitter_hist.svg")

    log.debug("Jitter Scatter")
    jitter_scatter = df.plot(
        x="packet_index",
        y="jitter",
        xlabel="Packet index",
        ylabel="Jitter / ms",
        kind="scatter",
        grid=True,
    ).get_figure()

    jitter_scatter.savefig(plot_path / "jitter_scatter.png")
    jitter_scatter.savefig(plot_path / "jitter_scatter.svg")

    log.debug("Jitter Line")
    jitter_line = df.plot(
        x="packet_index",
        y="jitter",
        xlabel="Packet index",
        ylabel="Jitter / ms",
        kind="line",
        grid=True,
    ).get_figure()

    jitter_line.savefig(plot_path / "jitter_line.png")
    jitter_line.savefig(plot_path / "jitter_line.svg")

    log.info("Jitter: Done!")

    if "latency" in results.keys():

        log.info("Latency: Plotting..")

        log.debug("Latency Histogram")

        latency_hist = df.plot(
            y="latency",
            xlabel="Added latency / ms",
            ylabel="Count",
            kind="hist",
            grid=True,
        ).get_figure()
        latency_hist.savefig(plot_path / "latency_hist.png")
        latency_hist.savefig(plot_path / "latency_hist.svg")

        log.debug("Latency Scatter")

        latency_scatter = df.plot(
            x="packet_index",
            y="latency",
            xlabel="Packet index",
            ylabel="Added latency / ms",
            kind="scatter",
            grid=True,
        ).get_figure()

        latency_scatter.savefig(plot_path / "latency_scatter.png")
        latency_scatter.savefig(plot_path / "latency_scatter.svg")

        log.debug("Latency Line")

        latency_line = df.plot(
            x="packet_index",
            y="latency",
            xlabel="Packet index",
            ylabel="Added latency / ms",
            kind="line",
            grid=True,
        ).get_figure()

        latency_line.savefig(plot_path / "latency_line.png")
        latency_line.savefig(plot_path / "latency_line.svg")

        log.info("Latency: Done!")

    log.info(f"All Done. Plots are saved in: {plot_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

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

    log = logging.getLogger("client")
    log.addHandler(logging.StreamHandler())

    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    json_path = pathlib.Path(args.json_path).resolve()
    plot_path = pathlib.Path(args.plot_path).resolve()

    plot(log=log, json_path=json_path, plot_path=plot_path)

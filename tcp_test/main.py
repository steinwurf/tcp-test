import argparse
import atexit
import os

from setup import setup, clean_up

default_packet_losses = [i / 2 for i in range(0, 4)]


def test_session():
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

    atexit.register(clean_up)

    for loss in default_packet_losses:
        setup()

        os.system(
            f"ip netns exec server tc qdisc add dev server_link root netem delay {args.server_latency}ms loss {loss}%"
        )
        os.system(
            f"ip netns exec client tc qdisc add dev client_link root netem delay {args.client_latency}ms"
        )

        os.system(
            f"gnome-terminal -- ip netns exec server python3 tcp_test/server.py --packets {args.packets} --throughput {args.throughput} --rely {args.rely}"
        )

        os.system(
            f"ip netns exec client python3 tcp_test/client.py --mode {args.mode} --packets {args.packets} --server-latency {args.server_latency} --client-latency {args.client_latency} --packet-loss {loss} --throughput {args.throughput} --rely {args.rely}"
        )

        clean_up()


if __name__ == "__main__":
    test_session()

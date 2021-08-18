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
        "--rely-path",
        type=str,
        help="The path to the Rely-app binary",
        default="",
    )

    args = parser.parse_args()

    atexit.register(clean_up)

    for loss in default_packet_losses:

        if not loss == default_packet_losses[0]:
            clean_up()

        setup()

        os.system(
            f"sudo ip netns exec server tc qdisc add dev server_link root netem delay {args.server_latency}ms loss {loss}%"
        )
        os.system(
            f"sudo ip netns exec client tc qdisc add dev client_link root netem delay {args.client_latency}ms"
        )

        if args.rely_path:
            os.system(
                f"sudo gnome-terminal -- ip netns exec server {args.rely_path} tun --local_endpoint 10.0.0.1:5000 --remote_endpoint 10.0.0.2:5000 --tunnel_ip 11.11.11.11"
            )
            os.system(
                f"sudo gnome-terminal -- ip netns exec client {args.rely_path} tun --local_endpoint 10.0.0.2:5000 --remote_endpoint 10.0.0.1:5000 --tunnel_ip 11.11.11.22"
            )
            rely = "true"

        else:
            rely = "false"

        os.system(
            f"sudo gnome-terminal -- ip netns exec server python3 tcp_test/server.py --packets {args.packets} --throughput {args.throughput} --rely {rely}"
        )

        os.system(
            f"sudo ip netns exec client python3 tcp_test/client.py --mode {args.mode} --packets {args.packets} --server-latency {args.server_latency} --client-latency {args.client_latency} --packet-loss {loss} --throughput {args.throughput} --rely {rely}"
        )


if __name__ == "__main__":
    test_session()

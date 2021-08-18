import os


def setup():
    os.system("ip netns add server")
    os.system("ip netns add client")

    os.system("ip link add server_link type veth peer name client_link")

    os.system("ip link set 'server_link' netns 'server'")
    os.system("ip link set 'client_link' netns 'client'")

    os.system("ip netns exec server ip addr add 10.0.0.1/24 dev server_link")
    os.system("ip netns exec client ip addr add 10.0.0.2/24 dev client_link")

    os.system("ip netns exec server ip link set dev server_link up")
    os.system("ip netns exec client ip link set dev client_link up")

    os.system("ip netns exec server ip link set dev lo up")
    os.system("ip netns exec client ip link set dev lo up")


def clean_up():
    os.system("ip netns delete client && ip netns delete server")

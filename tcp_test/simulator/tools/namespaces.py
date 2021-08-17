import os
import atexit


def create_namespaces():

    os.system("ip netns add server")
    os.system("ip netns add client")


def create_veth():

    os.system("ip link add server type veth peer name client")

    os.system("ip link set 'server' netns 'server'")
    os.system("ip link set 'client' netns 'client'")


def set_namespace_ip(ip_addr_1, port_1, ip_addr_2, port_2):

    os.system(f"ip netns exec server ip addr add {ip_addr_1}/{port_1} dev server")
    os.system(f"ip netns exec client ip addr add {ip_addr_2}/{port_2} dev client")


def open_links():

    os.system("ip netns exec server ip link set dev server up")
    os.system("ip netns exec client ip link set dev client up")

    os.system("ip netns exec server ip link set dev lo up")
    os.system("ip netns exec client ip link set dev lo up")


def remove_namespaces():

    os.system("ip netns delete server && ip netns delete client")


def setup(ip_addr_1, port_1, ip_addr_2, port_2):

    create_namespaces()
    create_veth()
    set_namespace_ip(ip_addr_1, port_1, ip_addr_2, port_2)
    open_links()

    os.system("ip addr")


if __name__ == "__main__":
    ip_addr_1 = "10.0.0.1"
    ip_addr_2 = "10.0.0.2"
    port = "24"
    setup(ip_addr_1, port, ip_addr_2, port)

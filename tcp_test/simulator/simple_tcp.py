import struct
import socket
import atexit
import time


def calculate_interval(packet_size: int, throughput: float or int):
    return packet_size / throughput


def header_size():
    return struct.calcsize("Q")


def write_header(now):
    return bytearray(struct.pack("<Q", now))


def read_header(header):
    assert len(header) >= header_size()
    return struct.unpack("<Q", header[: header_size()])


class Client(object):
    def __init__(self, log, ip_address, port, packet_bytes, packets):
        """Creates a simple client to receive packets from the simple server.

        :param ip_address:   The server IP-address
        :param port:         The server port
        :param packet_bytes: The size of each packet sent
        :param packets:      The amount of packets sent

        """

        self.log = log
        self.packet_bytes = packet_bytes
        self.packets = packets
        self.ip_address = ip_address
        self.port = port

        self.latency = []
        self.throughput = []

    def run(self):

        client = socket.socket()

        server_address = (self.ip_address, self.port)

        client.connect(server_address)
        client.sendall(bytearray("Hello, Server", "utf-8"))

        stats = {"byte_count": 0}

        packets_received = 0

        while packets_received < self.packets:
            data = client.recv(1400, socket.MSG_WAITALL)
            stats["byte_count"] += self.packet_bytes

            server_time = read_header(data)
            client_time = int(time.time_ns() / 1000000)
            elapsed_time = client_time - server_time

            self.latency.append(elapsed_time)
            self.throughput.append(
                self.packet_bytes / (elapsed_time / 1000) / (1024 * 1024)
            )

            packets_received += 1

        client.sendall(bytearray("Received All", "utf-8"))
        client.close()

    def save_results(self):
        return {"packets_latency": self.latency, "throughputs": self.throughput}


class Server(object):
    def __init__(self, log, ip_address, port, packet_bytes, throughput, packets):
        """Creates a simple client to receive packets from the simple server.

        :param ip_address:   The server IP-address
        :param port:         The server port
        :param packet_bytes: The size of each packet sent
        :param packets:      The amount of packets sent
        :param throughput:   The throughput of the TCP stream in B/s

        """

        self.log = log
        self.packet_bytes = packet_bytes
        self.packets = packets
        self.throughput = throughput
        self.ip_address = ip_address
        self.port = port

    def run(self):
        server = socket.socket()

        server_address = (self.ip_address, self.port)

        server.bind(server_address)

        server.listen(1)

        interval = calculate_interval(self.packet_bytes, self.throughput)

        client, client_address = server.accept()

        packets_sent = 0

        data = client.recv(1400).decode()

        if not data:
            return

        while packets_sent < self.packets:
            data = bytearray(self.packet_bytes)
            server_time = int(time.time_ns() / 1000000)
            struct.pack_into("<Q", data, 0, server_time)

            client.sendall(data)
            packets_sent += 1
            time.sleep(interval)

        data = client.recv(1400).decode()

        server.close()

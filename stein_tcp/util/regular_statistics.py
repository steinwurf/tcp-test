from abc import ABC, abstractmethod
import logging


class Statistics(ABC):
    def __init__(self, log: logging.Logger):
        self.log = log
        super().__init__()

    @abstractmethod
    def add_result(
        self,
        server_time: float,
        client_time: float,
        bytes_received: int,
    ):
        pass

    @abstractmethod
    def result(self) -> dict[str, int] | dict[str, list[float]]:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class PacketStatistics(Statistics):
    def __init__(self, log: logging.Logger):
        self.bytes_received = 0
        self.packets_received = 0
        self.log = log

    def add_result(
        self,
        server_time: float,
        client_time: float,
        bytes_received: int,
    ):

        self.log.debug(f"Added packet result")
        self.bytes_received += bytes_received
        self.packets_received += 1

    def result(self) -> dict[str, int]:
        results = {
            "packets_received": self.packets_received,
            "bytes_received": self.bytes_received,
        }
        return results

    def __str__(self) -> str:

        return f"Packets = {self.packets_received}, Total Bytes = {self.bytes_received}"


class JitterStatistics:
    def __init__(self, log: logging.Logger):
        self.server_time = []
        self.client_time = []

        # Jitter attributes
        self.jitter = []
        self.max_jitter_samples = 16
        self.current_elapsed = 0

        self.log = log
        self.start_time = None

    def add_result(
        self,
        server_time: float,
        client_time: float,
        bytes_received: int,
    ):

        self.log.debug(f"Added jitter result")

        self.server_time.append(server_time)
        self.client_time.append(client_time)
        self.calculate_jitter()

    def calculate_jitter(self):

        if len(self.server_time) == 1:
            self.jitter.append(0)
            self.current_elapsed = self.client_time[-1] - self.server_time[-1]
            return

        previous_jitter = self.jitter[-1]

        elapsed_now = self.client_time[-1] - self.server_time[-1]

        difference = elapsed_now - self.current_elapsed

        self.current_elapsed = elapsed_now

        if difference < 0:
            difference = -difference

        current_jitter = previous_jitter + (1 / self.max_jitter_samples) * (
            difference - previous_jitter
        )

        self.jitter.append(current_jitter)

    def result(self) -> dict[str, list[float]]:
        return {"jitter": self.jitter}

    def __str__(self):

        return f"Jitter = {self.jitter[-1]} ms"


class LatencyStatistics:
    def __init__(self, log: logging.Logger):
        self.server_time: list[float] = []
        self.client_time: list[float] = []

        # Only used with synchronized clocks
        self.latency: list[float] = []

        self.log = log
        self.start_time: float = None

    def add_result(self, server_time, client_time, bytes_received):

        self.log.debug(f"Added latency result")

        self.server_time.append(server_time)
        self.client_time.append(client_time)
        self.calculate_latency()

    def calculate_latency(self):

        self.latency.append(self.client_time[-1] - self.server_time[-1])

    def result(self):
        return {"latency": self.latency}

    def __str__(self):
        return f"Latency = {self.latency[-1]} ms"

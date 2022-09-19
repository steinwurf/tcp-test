import logging

from .regular_statistics import Statistics


class ConsoleStatistics:
    def __init__(
        self,
        log: logging.Logger,
        statistics: Statistics,
        report_interval=100,
    ):
        self.statistics = statistics
        self.log = log
        self.iterations = 0
        self.report_interval = report_interval

    def add_result(
        self,
        server_time: float,
        client_time: float,
        bytes_received: int,
    ):

        self.log.debug(f"Added result")

        self.statistics.add_result(server_time, client_time, bytes_received)

        self.iterations += 1

        if (self.iterations % self.report_interval) == 0:
            self.log.info(f"{self.statistics}")

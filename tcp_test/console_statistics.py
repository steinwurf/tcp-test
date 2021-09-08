class ConsoleStatistics:
    def __init__(self, log, statistics):
        self.statistics = statistics
        self.log = log
        self.iterations = 0

    def add_result(self, server_time, client_time, bytes_received):

        self.log.debug(f"Added result")

        self.statistics.add_result(server_time, client_time, bytes_received)

        self.iterations += 1

    def report(self):

        self.log.info(f"{self.statistics}")

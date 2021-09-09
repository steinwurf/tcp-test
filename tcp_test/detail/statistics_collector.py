class StatisticsCollector:
    def __init__(self, collectors: list, report_interval):
        self.collectors = collectors
        self.report_interval = report_interval

    def add_result(self, server_time, client_time, bytes_received):
        for collector in self.collectors:
            collector.add_result(server_time, client_time, bytes_received)

    def report(self):
        # If it is not time to report, then don't
        if self.collectors[0].iterations % self.report_interval != 0:
            return

        for collector in self.collectors:
            collector.report()

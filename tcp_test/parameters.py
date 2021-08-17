import addict
import logging
import simulator


def MB_to_B(mb_number):
    return mb_number * 1024 * 1024


def B_to_MB(b_number):
    return b_number / (1024 * 1024)


def default_parameters():

    parameters = addict.Dict()
    parameters.plot.legends.no_rely = "No Rely"
    parameters.plot.legends.rely = "Rely"
    parameters.plot.colors.no_rely = "#00cc66"
    parameters.plot.colors.rely = "#386cb0"

    parameters.experiments = []

    experiment = addict.Dict()
    mb_per_second = 1

    experiment.runs = 1
    experiment.packets = 1000
    experiment.link_latency = 60
    experiment.throughput = MB_to_B(mb_per_second)
    experiment.loss = [i for i in range(0.5, 2.5, 0.5)]
    experiment.packet_bytes = 100
    assert experiment.packet_bytes <= 1400
    experiment.client_ip = "10.0.0.1"
    experiment.server_ip = "10.0.0.2"
    experiment.port = 24
    experiment.client_tunnel_ip = "11.11.11.22"
    experiment.server_tunnel_ip = "11.11.11.11"
    experiment.tunnel_port = 5000

    parameters.experiments.append(experiment)

    return parameters


def description(experiment):
    tp_unit = "MB/s"

    packets = experiment.packets
    runs = experiment.runs
    throughput = B_to_MB(experiment.throughput)
    latency = experiment.link_latency

    if throughput > 1024:
        tp_unit = "GB/s"
        throughput = throughput / 1024

    text = f"""Packets sent = {packets}
    Throughput = {throughput} {tp_unit}
    Link-latency = {latency} ms
    Runs = {runs}"""


def run_experiment(experiment):

    log = logging.getLogger("simulation")
    log.addHandler(logging.StreamHandler)
    log.setLevel(logging.INFO)

    simple_session = simulator.simple

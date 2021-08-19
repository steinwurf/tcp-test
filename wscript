#! /usr/bin/env python
# encoding: utf-8

import os
import sys
import hashlib

top = "."

VERSION = "0.0.0"


def options(opt):
    pass

    opt.add_option(
        "--mode",
        help="The mode for data collection. histogram or throughput",
        default="histogram",
    )
    opt.add_option(
        "--packets",
        help="The number of packet to receive",
        default=10000,
    )
    opt.add_option(
        "--server-latency",
        help="The delay from the server to the client in ms",
        default=60,
    )
    opt.add_option(
        "--client-latency",
        help="The delay from the client to the server in ms",
        default=60,
    )
    opt.add_option(
        "--throughput",
        help="The throughput from the server to the client in MB/s",
        default=1,
    )
    opt.add_option(
        "--rely-path",
        help="The path to the Rely-app binary",
        action="store",
    )


def _create_venv(ctx):

    requirements_txt = os.path.join("requirements.txt")
    requirements_in = os.path.join("requirements.in")

    if not os.path.isfile(requirements_txt):
        with ctx.create_virtualenv() as venv:
            venv.run("python -m pip install pip-tools")
            venv.run(
                f"pip-compile {requirements_in} " f"--output-file {requirements_txt}"
            )

    # Hash the requirements.txt
    sha1 = hashlib.sha1(open(requirements_txt, "r").read().encode("utf-8")).hexdigest()[
        :6
    ]

    # venv name
    name = f"venv-{sha1}"

    # Create the venv
    if os.path.isdir(name):
        # If it already exist we should already have installed everything
        pip_install = False
    else:
        pip_install = True

    venv = ctx.create_virtualenv(name=name, overwrite=False)

    if pip_install:
        venv.env["PIP_IGNORE_INSTALLED"] = ""
        venv.run(f"python -m pip install -r {requirements_txt}")

    return venv


def run(ctx):

    mode = f"--mode {ctx.options.mode}"
    packets = f"--packets {ctx.options.packets}"
    server_latency = f"--server-latency {ctx.options.server_latency}"
    client_latency = f"--client-latency {ctx.options.client_latency}"
    throughput = f"--throughput {ctx.options.throughput}"

    options = f"{mode} {packets} {server_latency} {client_latency} {throughput}"

    if ctx.options.rely_path:
        rely = f" --rely-path {ctx.options.rely_path}"
        options += rely

    venv = _create_venv(ctx)

    venv.run(f"python3 tcp_test/main.py {options}")

    if ctx.options.mode == "throughput":
        venv.run(f"python3 tcp_test/plot_throughput.py {throughput}")

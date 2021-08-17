#! /usr/bin/env python
# encoding: utf-8

import os
import sys
import hashlib

top = "."

VERSION = "0.0.0"


def options(opt):
    pass


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


def run_netns(ctx):

    venv = _create_venv(ctx)

    venv.run("python3 tcp_test/simulator/tools/namespaces.py")

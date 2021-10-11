import io
import os
from tcp_test import __version__
from setuptools import setup, find_packages


cwd = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(cwd, "README.rst"), encoding="utf-8") as fd:
    long_description = fd.read()

setup(
    name="tcp-test",
    description="A tool for running different setups of a TCP transmission session.",
    author="Steinwurf ApS",
    author_email="contact@steinwurf.com",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    version=__version__,
    url="https://github.com/steinwurf/tcp-test",
    packages=["tcp_test", "tcp_test.detail"],
    install_requires=["matplotlib", "pandas"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD 3-Clause",
        "Operating System :: Ubuntu",
    ],
    entry_points={"console_scripts": ["tcp-test = tcp_test.main:main"]},
)

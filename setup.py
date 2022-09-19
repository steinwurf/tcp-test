from importlib.metadata import entry_points
from setuptools import setup

setup(
    name="stein_tcp",
    version="0.0.1",
    description="TCP client/server test tool",
    url="http://github.com/steinwurf/tcp-test",
    author="Steinwurf ApS",
    license="BSD-3-Clause",
    packages=["stein_tcp", "stein_tcp.util"],
    entry_points={
        "console_scripts": [
            "stein-net = stein_tcp.__main__:network_cli",
            "stein-iperf = stein_tcp.__main__:iperf_cli",
            "stein-client = stein_tcp.__main__:client_cli",
            "stein-server = stein_tcp.__main__:server_cli",
            "stein-plot = stein_tcp.__main__:plot_cli",
        ]
    },
    install_requires=[
        "pandas>=1.0.0,<2.0.0",
        "matplotlib>=3.0.0,<4.0.0",
    ],
    extras_require={
        "dev": [
            "black",
        ]
    },
    platforms=["linux"],
    zip_safe=False,
)

from importlib.metadata import entry_points
from setuptools import find_packages, setup


setup(
    name="stein-tcp",
    version="0.0.1",
    description="TCP client/server test tool",
    url="http://github.com/steinwurf/tcp-test",
    author="Steinwurf ApS",
    license="BSD-3-Clause",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "stein-tcp=stein_tcp.__main__:main",
            "stein-net = stein_tcp.network:main",
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

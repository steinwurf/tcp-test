===================
TCP Testing (Linux)
===================

This repo is Steinwurf's public TCP-testing library, used to showcase the power of Rely utilized under a TCP stream.

Dependencies
------------

Set up a virtual environment and install all the dependencies with::

    pip install -r requirements.txt

Usage
-----

To run the default setup use the following commands from the root of the tcp-test directory::

    python3 waf run

The waf script takes several arguments which can be seen by calling the waf help::

    python3 waf -h

The arguments are found in the "Options" section starting with "--mode".

There are other fixed parameters like Rely's repair interval and target, as well as the packet losses to test at. These can be found in the top part of main.py

With Rely
---------

If you wish to run a Rely tunnel underneath the TCP connection, you must have cloned and built the rely-app::

    git clone git@github.com:steinwurf/rely-app.git
    cd rely-app
    python3 waf configure
    python3 waf

In the tcp-test root, you can then provide the path to the rely-app binary from the command-line::

    python3 waf run --rely-path path/to/rely-app/build/linux/app/rely


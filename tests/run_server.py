#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
run_server
----------------------------------

Run a local HTTP server for testing purposes
"""

from contextlib import contextmanager
import os
import sys
from subprocess import Popen


def run_server(port=8000):
    with chdir('example-site'):
        if sys.version_info[0] == 2:
            command = 'python -m SimpleHTTPServer 8000'
        else:
            command = 'python -m http.server --bind localhost 8000'
        process = Popen(command.split())
    return process


def stop_server(process):
    process.terminate()


@contextmanager
def chdir(new_dir):
    old_dir = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(old_dir)

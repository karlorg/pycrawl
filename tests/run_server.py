#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
run_server
----------------------------------

Run a local HTTP server for testing purposes
"""

from contextlib import contextmanager
import multiprocessing
import os
import socketserver
try:
    from http.server import SimpleHTTPRequestHandler
except:
    from SimpleHTTPServer import SimpleHTTPRequestHandler


def run_server(port=8000):
    with chdir('example-site'):
        httpd = socketserver.TCPServer(("", port), SimpleHTTPRequestHandler)
        process = multiprocessing.Process(target=httpd.serve_forever)
        process.start()
    return (httpd, process)


def stop_server(server):
    httpd, process = server
    httpd.shutdown()  # XXX: blocks forever
    process.terminate()


@contextmanager
def chdir(new_dir):
    old_dir = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(old_dir)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pycrawl
----------------------------------

Tests for `pycrawl` module.
"""

import errno
from functools import wraps
import os
import re
import shutil
import time
import unittest
try:  # Python 3
    from urllib.parse import urlparse
except:  # Python 2
    from urlparse import urlparse

import bs4

from tests.run_server import run_server, stop_server
from pycrawl import pycrawl


def run_main_with_url(url):
    """Run main on the given URL, then delete the downloaded files after."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            argv = ['pycrawl.py', url]
            try:
                pycrawl.main(argv)
                f(*args, **kwargs)
            finally:
                # remove created download dir
                try:
                    basename = urlparse(url).hostname
                    shutil.rmtree(basename)
                except OSError as e:
                    if e.errno == errno.ENOENT:
                        pass
                    else:
                        raise
        return wrapper
    return decorator


class TestPycrawl(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = run_server()
        time.sleep(0.5)  # give it time to start up

    @classmethod
    def tearDownClass(cls):
        stop_server(cls.server)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @run_main_with_url('http://nonexistentsite.nes/badpath')
    def test_nonexistent_url(self):
        self.assertFalse(
            os.path.isfile('nonexistentsite.nes/badpath'))

    @run_main_with_url('http://localhost:8000/Python_logo_100x100.jpg')
    def test_non_html_url(self):
        self.assertTrue(os.path.isfile('localhost/Python_logo_100x100.jpg'))

    @run_main_with_url('http://localhost:8000')
    def test_valid_url_creates_dir_and_file(self):
        with open('localhost/__root__') as f:
            document = bs4.BeautifulSoup(f)
        self.assertTrue(bool(document.find(text=re.compile("Text"))))


if __name__ == '__main__':
    unittest.main()

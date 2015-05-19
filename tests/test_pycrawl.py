#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pycrawl
----------------------------------

Tests for `pycrawl` module.
"""

import contextlib
import errno
import os
import shutil
import unittest
try:  # Python 3
    from urllib.parse import urlparse
except:  # Python 2
    from urlparse import urlparse

import bs4

from pycrawl import pycrawl


class TestPycrawl(unittest.TestCase):

    def setUp(self):
        pass

    @contextlib.contextmanager
    def run_main_with_url(self, url):
        argv = ['pycrawl.py', url]
        try:
            pycrawl.main(argv)
            yield
        finally:
            try:
                basename = urlparse(url).hostname
                shutil.rmtree(basename)
            except OSError as e:
                if e.errno == errno.ENOENT:
                    pass
                else:
                    raise

    def test_nonexistent_url(self):
        with self.run_main_with_url('http://nonexistentsite.nes/badpath'):
            pass  # does not raise

    def test_non_html_url(self):
        with self.run_main_with_url(
                'http://static.tvtropes.org/namespace8.png'):
            pass  # does not raise

    def test_valid_url_creates_dir_and_file(self):
        with self.run_main_with_url('http://outpostdaria.info'):
            self.assertTrue(os.path.isdir('outpostdaria.info'))
            self.assertTrue(os.path.isfile('outpostdaria.info/__root__'))
            with open('outpostdaria.info/__root__') as f:
                bs = bs4.BeautifulSoup(f)
                self.assertTrue(bool(bs.find(text="Daria")))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()

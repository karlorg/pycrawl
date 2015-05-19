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

    def test_valid_url(self):
        with self.run_main_with_url('http://www.bbc.co.uk/sitemap.xml'):
            pass  # does not raise

    def test_nonexistent_url(self):
        with self.run_main_with_url('http://nonexistentsite.nes/badpath'):
            pass  # does not raise

    def test_non_html_url(self):
        with self.run_main_with_url(
                'http://static.tvtropes.org/namespace8.png'):
            pass  # does not raise

    def test_creates_dir(self):
        with self.run_main_with_url('http://outpostdaria.info'):
            self.assertTrue(os.path.isdir('outpostdaria.info'))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()

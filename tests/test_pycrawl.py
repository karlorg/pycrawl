#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pycrawl
----------------------------------

Tests for `pycrawl` module.
"""

import unittest

from pycrawl import pycrawl


class TestPycrawl(unittest.TestCase):

    def setUp(self):
        pass

    def test_valid_url(self):
        argv = ['pycrawl.py', 'http://www.bbc.co.uk/sitemap.xml']
        pycrawl.main(argv)  # should not raise

    def test_nonexistent_url(self):
        argv = ['pycrawl.py', 'http://nonexistentsite.nes/badpath']
        pycrawl.main(argv)  # should not raise

    def test_non_html_url(self):
        argv = ['pycrawl.py', 'http://static.tvtropes.org/namespace8.png']
        pycrawl.main(argv)  # should not raise

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()

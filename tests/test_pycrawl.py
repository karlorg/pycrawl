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

    def test_something(self):
        argv = ['pycrawl.py', 'http://www.bbc.co.uk/sitemap.xml']
        pycrawl.main(argv)  # should not raise

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()

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
    def test_valid_url_downloads_site(self):
        with open('localhost/__root__') as f:
            root = bs4.BeautifulSoup(f)
        self.assertTrue(bool(root.find(text=re.compile("Text"))))
        # check external link
        ext_link = root.find('a', text=re.compile("remote"))['href']
        self.assertEqual(urlparse(ext_link).hostname, 'www.bbc.co.uk',
                         "external links are unchanged")

        # now try a page linked from the first
        with open('localhost/local-relative.html') as f:
            relative = bs4.BeautifulSoup(f)
        self.assertTrue(bool(relative.find(text=re.compile("relative"))))
        # check link in index page
        rel_link = root.find('a', text=re.compile("relative"))['href']
        self.assertIsNone(urlparse(rel_link).hostname,
                          "relative links are unchanged")

        # and one linked via an explicit local domain
        with open('localhost/local-explicit.html') as f:
            explicit = bs4.BeautifulSoup(f)
        self.assertTrue(bool(explicit.find(text=re.compile("explicit"))))
        # check link in index page
        abs_link = root.find('a', text=re.compile("explicit"))['href']
        self.assertIsNone(urlparse(abs_link).hostname,
                          "absolute local links are changed to relative")

        # the image used on the front page should also be downloaded
        self.assertTrue(os.path.isfile('localhost/Python_logo_100x100.jpg'))
        # check link in index page
        img_src = root.find('img')['src']
        self.assertIsNone(urlparse(img_src).hostname,
                          "img src URLs are changed to relative")

        # mailto: links should not be downloaded
        self.assertFalse(os.path.isfile('localhost/nobody@nowhere.com'))


if __name__ == '__main__':
    unittest.main()

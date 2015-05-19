#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import os
import sys
try:  # Python 3
    from urllib import robotparser
    from urllib.parse import urlparse
except ImportError:  # Python 2
    import robotparser
    from urlparse import urlparse

import bs4
import requests


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        url = argv[1]
    except IndexError:
        print("Usage: {} URL".format(sys.argv[0]))
        sys.exit(1)
    basename = urlparse(url).hostname
    try:
        os.makedirs(basename)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(basename):
            pass
        else:
            raise
    print(process_url(url))


def process_url(url):
    if not can_robots_fetch(url):
        return []
    parsed_url = urlparse(url)
    basename = parsed_url.hostname
    path = parsed_url.path[1:]  # strip leading /
    if not path:
        path = '__root__'
    filename = os.path.join(basename, path)
    response = requests.get(url)
    if response.headers['content-type'] == 'text/html':
        filemode = 'w'
        file_content = response.text
        links = links_from_data(response.text)
    else:
        filemode = 'wb'
        file_content = response.content
        links = []
    with open(filename, filemode) as f:
        f.write(file_content)
    return links


def links_from_data(data):
    bs = bs4.BeautifulSoup(data)
    result = [tag['href'] for tag in bs.find_all('a')]
    return result


def can_robots_fetch(url):
    parsed_url = urlparse(url)
    robots_url_obj = parsed_url._replace(path='/robots.txt')
    robots_url = robots_url_obj.geturl()
    rp = robotparser.RobotFileParser(robots_url)
    try:
        # the following does not error on missing robots.txt files
        rp.read()
        if not rp.can_fetch("*", url):
            return False
    except:
        return False
    return True


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    print(links_from_url(url))


def links_from_url(url):
    if not can_robots_fetch(url):
        return []
    return links_from_data(requests.get(url).text)


def links_from_data(data):
    bs = bs4.BeautifulSoup(data)
    result = []
    for tag in bs.find_all('a'):
        result.append(tag['href'])
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

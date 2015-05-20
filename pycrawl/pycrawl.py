#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
import errno
import os
import sys
try:  # Python 3
    from urllib import robotparser
    from urllib.parse import urlparse
except ImportError:  # Python 2
    import robotparser
    from urlparse import urlparse
    str = unicode

import bs4
import requests
from requests.exceptions import ConnectionError


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        url = argv[1]
    except IndexError:
        print("Usage: {} URL".format(sys.argv[0]))
        sys.exit(1)

    create_download_dir(url)
    download_site(url)


def create_download_dir(url):
    basename = urlparse(url).hostname
    try:
        os.makedirs(basename)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(basename):
            pass
        else:
            raise


def download_site(root_url):
    pending_urls = {root_url}
    done_urls = set()
    root_netloc = urlparse(root_url).netloc
    while len(pending_urls) > 0:
        url = pending_urls.pop()
        done_urls.add(url)
        links = process_url_and_get_links(url)
        for link in links:
            parsed = urlparse(link)
            if parsed.hostname is None:
                parsed = parsed._replace(netloc=root_netloc, scheme='http')
                link = parsed.geturl()
            if parsed.netloc == root_netloc and link not in done_urls:
                # XXX: temporarily limit to fetching 10 urls so I can
                # test on live sites without being too much of a
                # nuisance
                if len(done_urls) < 10:
                    pending_urls.add(link)


def process_url_and_get_links(url):
    if not can_robots_fetch(url):
        return []
    try:
        response = requests.get(url)
    except ConnectionError:
        return []

    parsed_url = urlparse(url)
    basename = parsed_url.hostname
    path = parsed_url.path[1:]  # strip leading /
    if not path:
        path = '__root__'
    filename = os.path.join(basename, path)

    if response.headers['content-type'] == 'text/html':
        filemode = 'w'
        update_result = update_and_return_links(response.text, basename)
        file_content = update_result.data
        links = update_result.links
    else:
        filemode = 'wb'
        file_content = response.content
        links = []
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    with open(filename, filemode) as f:
        f.write(file_content)
    return links


UpdateResult = namedtuple('UpdateResult', ['data', 'links'])


def update_and_return_links(data, hostname):
    """Update and return local links in HTML."""
    soup = bs4.BeautifulSoup(data)
    links = set()

    def process_attrs(tagname, attrname):
        for tag in soup.find_all(tagname):
            try:
                attr = tag[attrname]
            except KeyError:
                continue
            parsed_attr = urlparse(attr)
            if parsed_attr.scheme == 'mailto':
                continue
            if parsed_attr.hostname == hostname:
                parsed_attr = parsed_attr._replace(scheme='', netloc='')
                attr = parsed_attr.geturl()
                tag[attrname] = attr
            links.add(attr)

    process_attrs('a', 'href')
    process_attrs('img', 'src')
    return UpdateResult(data=str(soup), links=links)


robots_txt_cache = {}


class AllowAllRobots(object):
    """Dummy RobotFileParser-alike that allows all paths"""
    def can_fetch(self, robot, path):
        return True


def can_robots_fetch(url):
    parsed_url = urlparse(url)
    robots_url_obj = parsed_url._replace(path='/robots.txt')
    robots_url = robots_url_obj.geturl()

    try:
        rp = robots_txt_cache[robots_url]
        return rp.can_fetch("*", url)
    except KeyError:
        try:
            response = requests.get(robots_url)
        except ConnectionError:
            # no robots.txt => assume robots are OK
            robots_txt_cache[robots_url] = AllowAllRobots()
            return True
        if response.status_code != 200:
            robots_txt_cache[robots_url] = AllowAllRobots()
            return True

        try:
            rp = robotparser.RobotFileParser(robots_url)
            rp.read()
            if not rp.can_fetch("*", url):
                robots_txt_cache[robots_url] = rp
                return False
        except:
            raise RuntimeError("unreadable robots.txt")
        robots_txt_cache[robots_url] = rp
        return True


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
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


logging.basicConfig(filename='log',
                    filemode='a',
                    level=logging.DEBUG)


def main(argv=None):
    if argv is not None:
        sys.argv = argv
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="the base URL to retrieve")
    parser.add_argument("-d", "--max-depth", type=int,
                        help="maximum recursion depth")
    args = parser.parse_args()

    download_site(args.url, args.max_depth)


def download_site(root_url, max_depth=None):
    root_netloc = urlparse(root_url).netloc
    pending_urls = [get_canonical_url(root_url)]
    done_urls = set()

    at_depth = 0
    while len(pending_urls) > 0:
        # at each level of recursion, we take all pending urls out of
        # the queue and loop over them
        urls = pending_urls
        pending_urls = []
        for url in urls:
            done_urls.add(url)

            # process the URL
            links = process_url_and_get_links(url)

            # no need to add pending links if we're at max recursion depth
            if max_depth is not None and at_depth >= max_depth:
                continue
            # normalize links from this URL and add to pending as appropriate
            for raw_link in links:
                link = get_canonical_url(raw_link, root_netloc=root_netloc)
                if (urlparse(link).netloc == root_netloc and
                        link not in done_urls):
                    pending_urls.append(link)
        at_depth += 1


def get_canonical_url(url, root_netloc=None):
    """Drop params, query and fragment; optionally add netloc to relative links.
    """
    parsed = urlparse(url)._replace(params='',
                                    query='',
                                    fragment='')
    if root_netloc is not None and parsed.hostname is None:
        parsed = parsed._replace(scheme='http', netloc=root_netloc)
    return parsed.geturl()


def process_url_and_get_links(url):
    if not can_robots_fetch(url):
        return []
    print("fetching {}".format(url))
    try:
        response = requests.get(url)
    except ConnectionError:
        return []

    hostname, filename = get_host_and_filename(url)

    if response.headers['content-type'] == 'text/html':
        filemode = 'w'
        file_content, links = get_content_and_links(response.text, hostname)
    else:
        filemode = 'wb'
        file_content = response.content
        links = []
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    with open(filename, filemode) as f:
        f.write(file_content)
    return links


def get_host_and_filename(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    path_str = parsed_url.path or '__root__'
    path = path_str.split('/')
    return (hostname, os.path.join(hostname, *path))


def get_content_and_links(data, hostname):
    """Update and return local links in HTML.

    ie. return an HTML document equivalent to the input, but with
    local links adjusted to work in a downloaded copy of the site.
    Also return a list of all link targets from this document.
    """
    soup = bs4.BeautifulSoup(data)
    links = []

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
            links.append(attr)

    process_attrs('a', 'href')
    process_attrs('img', 'src')
    try:
        return (str(soup), links)
    except RuntimeError:
        # can't render through BeautifulSoup; for now, just output the
        # original data with links unchanged
        return (data, links)


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

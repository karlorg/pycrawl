#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
try:  # Python 3
    from html.parser import HTMLParser
    from urllib import robotparser
    from urllib.parse import urlparse
except ImportError:  # Python 2
    from HTMLParser import HTMLParser
    import robotparser
    from urlparse import urlparse

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


class HTMLLinkFinder(HTMLParser):
    def __init__(self, *args, **kwargs):
        self.found_links = []
        HTMLParser.__init__(self, *args, **kwargs)

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        attr_dict = dict(attrs)
        try:
            self.found_links.append(attr_dict['href'])
        except:
            pass

    def reset(self):
        self.found_links = []
        HTMLParser.reset(self)


def links_from_url(url):
    parsed_url = urlparse(url)
    robots_url_obj = parsed_url._replace(path='/robots.txt')
    robots_url = robots_url_obj.geturl()
    rp = robotparser.RobotFileParser(robots_url)
    rp.read()
    if not rp.can_fetch("*", url):
        return []
    data = requests.get(url).text

    link_finder = HTMLLinkFinder()
    link_finder.feed(data)
    return link_finder.found_links


if __name__ == '__main__':
    main()

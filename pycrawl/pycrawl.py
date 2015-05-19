#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
try:
    from urllib import robotparser  # Python 3
    from urllib.parse import urlparse
except ImportError:
    import robotparser  # Python 2
    from urlparse import urlparse


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        url = argv[1]
    except IndexError:
        print("Usage: {} URL".format(sys.argv[0]))
        sys.exit(1)
    parsed_url = urlparse(url)
    robots_url_obj = parsed_url._replace(path='/robots.txt')
    robots_url = robots_url_obj.geturl()
    rp = robotparser.RobotFileParser(robots_url)
    rp.read()
    if rp.can_fetch("*", url):
        print("we're good")
    else:
        print("uh oh")

if __name__ == '__main__':
    main()

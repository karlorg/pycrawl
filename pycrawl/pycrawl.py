#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from urllib import robotparser  # Python 3
except ImportError:
    import robotparser  # Python 2


def main():
    rp = robotparser.RobotFileParser("http://www.tvtropes.com/robots.txt")
    rp.read()
    url = "http://www.tvtropes.com/pmwiki/pmwiki.php/Main/AcmeProducts"
    if rp.can_fetch("*", url):
        print("we're good")
    else:
        print("uh oh")

if __name__ == '__main__':
    main()

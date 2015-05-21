===============================
Python Webcrawler Thing
===============================

.. image:: https://img.shields.io/travis/karlorg/pycrawl.svg
        :target: https://travis-ci.org/karlorg/pycrawl

Three-day exercise project: slurp a website to local storage

This is an exercise created under the 'three day project paradigm'
described by Daniel Moniz in this PyCon talk:
https://www.youtube.com/watch?v=ohr6O78jGzs

Due to the three day limit, the functionality is very basic -- see below.

* Free software: BSD license

Usage
-----

Either run the script from the repo by creating a virtualenv,
installing requirements with pip and doing::

  ./pycrawl/pycrawl.py

Or you can install it (probably into a virtualenv, again) with::

  python setup.py install

and use the ``pycrawl`` script that becomes available.  Calling the
script with no arguments displays its usage.

Features
--------

* Downloads a given website's static content, following ``<a>`` and
  ``<img src="..">`` links within the same domain.

* Updates links to the same domain so that they will point to the
  downloaded copies of the files.

* Accepts a command line option to limit the depth to which links will
  be followed for downloading.

Bugs and ideas for extension
-------------------

Features that were not provided due to lack of time:

* Also download CSS and JS, and update links within CSS (eg. background images).

* If interrupted, save the necessary internal state to continue later.

* Do not update links to content that will not be downloaded due to a
  maximum recursion depth limit.

* For certain pages
  (eg. http://outpostdaria.info/essay/rl_daria_temporal_analysis_project.html),
  rendering the updated document using BeautifulSoup enters an
  infinite loop.  Currently the application just saves the original
  document unmodified in these cases; it would obviously be better to
  either fix this bug or work around it by changing the links by some
  other method.

* Some pages
  (eg. http://outpostdaria.info/essay/mq_the_running_gag_theory.html)
  become mangled after processing, losing formatting and gaining odd
  characters.  Possibly I've missed something involving the character
  encodings used to generate and save output?

===============================
stockbot
===============================

.. image:: https://img.shields.io/travis/ChrisPappalardo/stockbot.svg
        :target: https://travis-ci.org/ChrisPappalardo/stockbot

.. image:: https://img.shields.io/pypi/v/stockbot.svg
        :target: https://pypi.python.org/pypi/stockbot


Stock market analysis library written in Python.

* Copyright (C) 2016 by Chris Pappalardo <cpappala@yahoo.com>
* License: Creative Commons (CC) BY-NC-ND 4.0 https://creativecommons.org/licenses/by-nc-nd/4.0/
* Documentation: https://stockbot-lib.readthedocs.org/

Features
--------

* market data sourcing from Yahoo! and CNBC
* zipline data sourcing and performance analysis

Installation
------------

You must first build the `quantopian/zipline` Docker image with the following command::

  $ docker build -t quantopian/zipline https://github.com/quantopian/zipline.git#1.0.2

To create the stockbot Docker development container, simply run the following::

  $ docker-compose -f docker-compose-dev.yml up

Usage
-----

To run an algorithm, issue the following::

  $ docker-compose -f docker-compose-dev.yml run --rm stockbot zipline run -f /app/stockbot/algo/<file>

Use the `--start <YYYY-M-D>` and `--end <YYYY-M-D>` args to pass dates.  `-o /path/file.pickle`
to capture pickled results that can be used in python.

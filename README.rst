===============================
Stockbot
===============================

.. image:: https://img.shields.io/travis/ChrisPappalardo/stockbot.svg
        :target: https://travis-ci.org/ChrisPappalardo/stockbot

.. image:: https://img.shields.io/pypi/v/stockbot.svg
        :target: https://pypi.python.org/pypi/stockbot


Stock market analysis library written in Python.

* Copyright (C) 2016 by Chris Pappalardo <cpappala@yahoo.com>
* License: `Creative Commons (CC) BY-NC-ND 4.0
<https://creativecommons.org/licenses/by-nc-nd/4.0/>`_
* Documentation: https://stockbot-lib.readthedocs.org/


Features
--------

* Market data sourcing from Yahoo!, CNBC, and zipline bundles
* S&P500 stock listing scraper
* ADX, DI, and Stochastic technical indicators implemented using TA-lib
* Average Directional Movement Index (ADX) ranking for portfolios
* Trending and oscillating instrument trading algorithms for zipline


Installation
------------

Install the latest package with::

  $ pip install stockbot

The dependencies are not trivial and may not install properly on your system
through pip.  We recommend developing and deploying your projects that use
Stockbot in `Docker <http://www.docker.com>`_ containers with the necessary
packages pre-installed.

To do this, first build the `quantopian/zipline` Docker image using version
`1.1.1` of the source code with the following command::

  $ docker build -t quantopian/zipline https://github.com/quantopian/zipline.git#1.1.1

Then use a docker-compose configuration similar to Stockbot's production cluster
[here](docker-compose.yml).  Build your containers with::

  $ docker-compose build

To run Stockbot's trading algorithms in zipline and to use certain functions,
you will need to download a `quantopian-quandl` bundle::

  $ docker-compose run --rm stockbot zipline ingest -b quantopian-quandl


Usage
-----

Stockbot can provide you with a list of S&P500 stocks from 
`Wikipedia <https://en.wikipedia.org/wiki/List_of_S%26P_500_companies>`_::

   >>> from stockbot.core import get_sp500_list
   >>> get_sp500_list()
   [u'MMM', u'ABT', u'ABBV', u'ACN', u'ATVI', u'AYI', u'ADBE', ... u'ZTS']
   
To get a delayed quote from Yahoo! use `get_yahoo_quote`::
     
   >>> from stockbot.sources import get_yahoo_quote
   >>> get_yahoo_quote('YHOO')
   {'volume': 3405057, 'last': 41.0, 'symbol': 'YHOO', 'datetime': datetime.datetime(2016, 11, 22, 18, 0, tzinfo=<UTC>), 'high': 41.4, 'low': 40.83, 'open': 41.2, 'change': -0.11}

Or a real-time quote from CNBC using `get_cnbc_quote`::

   >>> from stockbot.sources import get_cnbc_quote
   >>> next(get_cnbc_quote('YHOO'))
   {'volume': 3528566, 'last': 41.04, 'symbol': u'YHOO', 'datetime': datetime.datetime(2016, 11, 22, 21, 0, tzinfo=<UTC>), 'high': 41.395, 'low': 40.83, 'open': 41.2, 'change': -0.07}

Note:: `get_cnbc_quote` returns a generator.

Stockbot returns quote data using a `dict` like object
`stockbot.marketdata.MarketData` that performs certain data and datetime
processing.

Historical data can be obtained from Yahoo! using `get_yahoo_hist`::
     
   >>> from stockbot.sources import get_yahoo_hist
   >>> get_yahoo_hist('YHOO')
   {'high': 41.48, 'last': 41.110001, 'datetime': datetime.datetime(2016, 11, 21, 21, 0, tzinfo=<UTC>), 'volume': 11338000, 'low': 40.939999, 'close': 41.110001, 'open': 41.439999}
   
Historical data can also be obtained from zipline bundles using the
`get_zipline_hist` function::

   >>> from stockbot.sources import get_zipline_hist
   >>> get_zipline_hist('YHOO', 'close', datetime.datetime(...))
   2016-01-04 00:00:00+00:00    31.41
   Freq: C, Name: Equity(3177 [YHOO]), dtype: float64

Look up symbols with `stockbot.sources.get_symbol` which searches Yahoo!
finance for the passed term.

Zipline trading algorithms that utilize the Directional Movement technical
indicator system are provided in `stockbot.algo`.  For example, the following
zipline trading algorithm would use ADX and DI to trade the top trending
stocks and Stochastic Oscillators to trade the top oscillating stocks in the
S&P 500 index::

   from logbook import Logger
   from stockbot.algo.core import (
       adx_init,
       trade_di,
       trade_so,
   )
   from stockbot.core import get_sp500_list

   def initialize(context):
       return adx_init(
           context,
           name='adx_di_so',
           top_rank=5,
           bot_rank=5,
           di_window=14,
           symbols=get_sp500_list(),
           log=Logger('Stockbot'),
       )

   def handle_data(context, data):
       # increment counter and log datetime
       context.i += 1
       context.adx['log'].info('processing %s' % context.get_datetime())

       # trade trending S&P500 stocks using the DI system
       trade_di(
           context,
           data,
           window=context.adx['di_window'],
           portfolio=[i for (i, adx) in context.adx['top']],
           capital_ppi=1.0/(len(context.adx['top'])+len(context.adx['bot'])),
           log=context.adx['log'],
       )

       # trade oscillating S&P500 stocks using the SO system
       trade_so(
           context,
           data,
           window=context.adx['di_window'],
           portfolio=[i for (i, adx) in context.adx['bot']],
           capital_ppi=1.0/(len(context.adx['top'])+len(context.adx['bot'])),
           log=context.adx['log'],
       )

To run this algorithm in a docker container, copy the code above into a file
and issue the following::

  $ docker-compose run --rm stockbot zipline run -f <file> --start <date> --end <date>

Use the the `<YYYY-M-D>` format for dates.  Use `-o /path/file.pickle` to
capture pickled results that can be used in python.

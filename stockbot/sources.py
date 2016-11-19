# -*- coding: utf-8 -*-

'''

The `sources` module provides functions and classes that are useful for:

- obtaining price quotes for symbols
- obtaining historical price information for symbols
- looking up symbols
- determining current market status (open/closed)

'''

###############################################################################


from collections import (MutableMapping, MutableSequence)
import csv
import datetime as dt
import json
import re
import sys
if sys.version_info > (3, 0): # pragma: no cover
    from urllib.parse import quote_plus
    from urllib.request import urlopen
else:
    from urllib import quote_plus
    from urllib2 import urlopen

from dateutil.parser import parse
from dateutil.tz import tzlocal
from pandas.tslib import Timestamp
import pytz
from zipline.assets._assets import Equity
from zipline.data.bundles.core import load
from zipline.data.data_portal import DataPortal
from zipline.utils.calendars import get_calendar

from .marketdata import MarketData


_YAHOO_QUOTE = {
    'source': (
        u'http://download.finance.yahoo.com/d/' +
        u'quotes.csv?s=%s&f=sl1d1t1c1ohgv&e=.csv'),
    'format': 'csv',
    'tz': 'America/New_York',
    'close': parse('4:00pm'),
    'mapping': [
        'symbol',
        'last',
        'date',
        'time',
        'change',
        'open',
        'high',
        'low',
        'volume'
    ],
}


_YAHOO_HIST = {
    'source': (
        u'http://ichart.finance.yahoo.com/' +
        u'table.csv?s=%s&d=11&e=31&f=9999&g=d&a=0&b=1&c=1900&ignore=.csv'
    ),
    'format': 'csv',
    'tz': 'America/New_York',
    'close': parse('4:00pm'),
    'mapping': [
        'date',
        'open',
        'high',
        'low',
        'close',
        'volume',
        'last'
    ],
}


_CNBC_QUOTE = {
    'source': u'http://data.cnbc.com/quotes/%s',
    'format': 'json',
    'tz': 'America/New_York',
    'close': parse('4:00pm'),
    'pattern': u'var quoteDataObj = (\[{.*?}\])',
    'mapping': {
        'symbol': 'symbol',
        'last': 'last',
        'change': 'change',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'volume': 'volume',
    },
}


_YAHOO_SEARCH = {
    'source': (
        u'http://d.yimg.com/aq/' +
        u'autoc?query=%s&region=US&lang=en-US'
    ),
    'format': 'json',
    'pattern': u'{"ResultSet":{"Query":".*?","Result":(\[.*?\])}}',
    'mapping': {
        'symbol': 'symbol',
        'name': 'name',
        'exchange': 'exch',
        'type': 'typeDisp',
    },
}


_YAHOO_STATUS_US = {
    'source': u'http://finance.yahoo.com',
    'format': 'raw',
    'pattern': u'>U\.S\. Markets (.*?)<',
}


_ZIPLINE_QUANDL_BUNDLE = {
    'name': 'quantopian-quandl',
    'cal': 'NYSE',
}


class DataError(Exception):
    '''
    Custom exception for data errors.
    '''

    def __init__(self, value):
        '''
        `DataError` constructor.

        :param:`value` the exception message
        '''

        self.value = value

    def __str__(self):
        return str(self.value)


def _get_data(symbol,
              source,
              format,
              tz=None,
              close=None,
              pattern=None,
              mapping=None,
              header=True):
    '''
    Gets price data for `:param symbol:` from `:param source` and
    returns a `MarketData` object with OHLC plus extended data.

    Timestamps are in UTC by default.

    :param symbol: the ticker symbol of the instrument we want to price
    :param source: the URL source of the data; can be http(s) or file
    :param format: the format of the incoming data, 'csv' 'json' 'raw'
    :param tz: the `pytz.timezone` timezone label of datetime data
    :param close: the default market close associated with `:param symbol:`
    :param pattern: an optional regex pattern to strip from response
    :param mapping: maps data to labels, either positional or associative
    :param header: assume the first line of a multi-line csv is the header
    :type symbol: `str`
    :type source: `str`
    :type format: `str`
    :type tz: `str` (default=None)
    :type close: `str` (default=None)
    :type pattern: `str` (default=None)
    :type mapping: `list` or `dict` (default=None)
    :type header: `bool` (default=True)
    :returns: a generator that yields objects for each timeseries node
    :rtype: `MarketData`
    :raises IOError: from urlopen if the connection cannot be made
    :raises DataError: if the returned data is blank or the regex fails
    :raises ValueError: if the UTF-8 encoding fails
    :raises:`ValueError` if `json.loads()` fails
    :raises:`AttributeError` if json elements are not `dict` or `list`

    .. warning:: `:param pattern:` and multi-line csv are mutually exclusive

    .. warning:: `:param mapping:` must be aligned `list` when `:param format:`
                 is 'csv'

    .. warning:: `:param mapping:` must be `dict` of (out, in) keys when
                 `:param format:` is 'json'

    .. warning:: 'json' data elements must be `dict` types

    :Example:

    >>> TODO
    '''

    # read lines from URL (http(s) or file); returns list of lines or exception
    source = source % quote_plus(symbol) if symbol else source
    data = urlopen(source).readlines()

    # strip regex pattern if passed
    if pattern:

        # collapse data list before applying regex
        data = re.compile(pattern, re.DOTALL).search(''.join(data))

        # extract matched pattern or raise exception
        data = data.group(1) if data.group else None
        if not data: # pragma: no cover
            raise DataError('regex on data failed to produce a result')

    # csv format: yield each line as a MarketData object with clean dt
    if format == 'csv':

        # if header, assume first line of multi-line list is the header
        if header and len(data) > 1:
            data.pop(0)

        for row in csv.reader(data):

            if len(row) != len(mapping): # pragma: no cover
                raise DataError('csv row length does not match mapping')

            yield MarketData(dict(zip(mapping, row))).clean_dt(tz, close)

    # json format: yield each element as a MarketData object with clean dt
    elif format == 'json':

        # decode json data; force top-level to list
        data = json.loads(data)
        data = [data] if not isinstance(data, MutableSequence) else data

        for o in data:

            if not isinstance(o, MutableMapping): # pragma: no cover
                raise DataError('json elements are not dicts')

            # replace keys
            o = dict(map(lambda (a, b): (a, o.get(b, None)), mapping.items()))

            yield MarketData(o).clean_dt(tz, close)

    # raw format: yield the raw result
    elif format == 'raw':

        yield data


def get_yahoo_quote(symbol):
    '''
    Gets a delayed price quote for :param:`symbol` from Yahoo! finance.

    :param:`symbol` the ticker symbol of the instrument we want to price
    :type:`symbol` `str`
    :returns: `MarketData` object with labeled price data
    :rtype:`pd.Series`
    :raises:`IOError`
    :raises:`DataError`
    :raises:`ValueError`
    :raises:`AttributeError`
    '''

    return next(_get_data(
        symbol,
        _YAHOO_QUOTE['source'],
        _YAHOO_QUOTE['format'],
        _YAHOO_QUOTE['tz'],
        _YAHOO_QUOTE['close'],
        mapping=_YAHOO_QUOTE['mapping'],
    ))


def get_yahoo_hist(symbol):
    '''
    Gets historical price data for :param:`symbol` from Yahoo! finance.

    :param:`symbol` the ticker symbol of the instrument we want to price
    :type:`symbol` `str`
    :returns: a `MarketData` obj generator of labeled price data
    :rtype:`pd.DataFrame`
    :raises:`IOError`
    :raises:`DataError`
    :raises:`ValueError`
    :raises:`AttributeError`
    '''

    return _get_data(
        symbol,
        _YAHOO_HIST['source'],
        _YAHOO_HIST['format'],
        _YAHOO_HIST['tz'],
        _YAHOO_HIST['close'],
        mapping=_YAHOO_HIST['mapping'],
    )

#    return pd.DataFrame(d).T


def get_cnbc_quote(symbol):
    '''
    Gets a real-time price quote for :param:`symbol` from CNBC.

    :param:`symbol` the ticker symbol of the instrument we want to price
    :type:`symbol` `str`
    :returns: `MarketData` object with labeled price data
    :rtype:`pd.Series`
    :raises:`IOError`
    :raises:`DataError`
    :raises:`ValueError`
    :raises:`AttributeError`
    '''

    return _get_data(
        symbol,
        _CNBC_QUOTE['source'],
        _CNBC_QUOTE['format'],
        _CNBC_QUOTE['tz'],
        _CNBC_QUOTE['close'],
        _CNBC_QUOTE['pattern'],
        _CNBC_QUOTE['mapping'],
    )


def get_symbol(symbol):
    '''
    Gets a list of securities containing :param:`symbol`.

    :param:`symbol` the symbol or name fragment to find
    :type:`search` `str`
    :returns: a `MarketData` obj generator of results
    :rtype: `list`
    :raises:`IOError`
    :raises:`DataError`
    :raises:`ValueError`
    :raises:`AttributeError`
    '''

    return _get_data(
        symbol,
        _YAHOO_SEARCH['source'],
        _YAHOO_SEARCH['format'],
        pattern=_YAHOO_SEARCH['pattern'],
        mapping=_YAHOO_SEARCH['mapping'],
    )


def get_status_US():
    '''
    Get the open/closed status of markets in the United States.

    :returns: a string with time remaining until close or 'closed'
    :rtype: `str` or `None`
    :raises:`IOError`
    :raises:`DataError`
    :raises:`ValueError`
    :raises:`AttributeError`
    '''

    return next(_get_data(
        '',
        _YAHOO_STATUS_US['source'],
        _YAHOO_STATUS_US['format'],
        pattern=_YAHOO_STATUS_US['pattern'],
    ))


def get_zipline_dp(bundle=None, calendar=None):
    '''
    Creates and returns a zipline data portal, used for symbol lookups and data

    `bundle` is a `zipline`BundleData` object (optional)
    `calendar` is a `zipline`ExchangeCalendar` object (optional)
    '''

    if bundle is None: bundle = load(_ZIPLINE_QUANDL_BUNDLE['name'])
    if calendar is None: calendar = get_calendar(_ZIPLINE_QUANDL_BUNDLE['cal'])

    return DataPortal(
        bundle.asset_finder,
        calendar,
        first_trading_day=bundle.equity_minute_bar_reader.first_trading_day,
        equity_minute_reader=bundle.equity_minute_bar_reader,
        equity_daily_reader=bundle.equity_daily_bar_reader,
        adjustment_reader=bundle.adjustment_reader,
    )


def get_zipline_hist(symbol,
                     field,
                     end_dt,
                     bar_count=1,
                     frequency='1d',
                     bundle=None,
                     calendar=None,
                     dp=None):
    '''
    Gets daily historical price data for :param:`symbol` from a zipline bundle.

    :param:`symbol` the ticker symbol of the instrument
    :type:`symbol` `str`
    :param:`field` the desired OHLC field
    :type:`field` `str`
    :param:`end_dt` the ending datetime of the series
    :type:`end_dt` `dt.datetime`
    :param:`bar_count` the number of points in the timeseries
    :type:`bar_count` `int`
    :param:`frequency` the frequency of the timeseries (e.g. "1d" or "1m")
    :type:`frequency` `str`
    :param:`bundle` a `zipline`ExchangeCalendar` object
    :type:`bundle` `zipline.data.bundles.core.BundleData`
    :param:`calendar` a `zipline` `BundleData` object
    :type:`calendar` `str`
    :returns:`pandas.DataFrame`
    :rtype:`pandas.DataFrame`
    :raises:`IOError`
    :raises:`DataError`
    :raises:`ValueError`
    :raises:`AttributeError`

    Snap a date to the calender with::

         get_calendar(cal).all_sessions.asof(Timestamp(end_dt))

    Get the last traded datetime for a symbol and calendar dt with::

         dp.get_last_traded_dt(
             dp.asset_finder.lookup_symbol(symbol, None),
             get_calendar(cal).all_sessions.asof(Timestamp(end_dt)),
             'daily',
         )

    Get the session index with::

         get_calendar(cal).all_sessions.searchsorted(Timestamp(end_dt))
    '''

    dp = get_zipline_dp(bundle, calendar) if dp is None else dp
    if type(symbol) is not Equity:
        symbol = dp.asset_finder.lookup_symbol(symbol, None)

    return dp.get_history_window(
        [symbol],
        Timestamp(end_dt),
        bar_count,
        frequency,
        field,
    ).iloc[:,0]

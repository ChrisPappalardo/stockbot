# -*- coding: utf-8 -*-

'''

sources
-------

provides functions and classes that are useful for sourcing market and other
data:

- obtaining price quotes for symbols
- obtaining historical price information for symbols
- looking up symbols
- determining current market status (open/closed)

'''

###############################################################################


from collections import (MutableMapping, MutableSequence)
import csv
import json
import re

from dateutil.parser import parse
from pandas.tslib import Timestamp
from six.moves.urllib.parse import quote_plus
from six.moves.urllib.request import urlopen
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
    custom exception for data errors
    '''

    def __init__(self, value):
        '''
        :param value: the exception information
        :type value: typically `str`
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
    Returns OHLC plus extended data for a given symbol.

    Note: Timestamps are in UTC by default.

    :returns: a generator that yields objects for each timeseries node
    :rtype: `MarketData`
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

    .. warning:: pattern and multi-line csv are mutually exclusive

    .. warning:: mapping must be aligned `list` when format is csv

    .. warning:: mapping must be `dict` of (out, in) keys when format is json

    .. warning:: json data elements must be `dict` types
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
        if not data:  # pragma: no cover
            raise DataError('regex on data failed to produce a result')

    # csv format: yield each line as a MarketData object with clean dt
    if format == 'csv':

        # if header, assume first line of multi-line list is the header
        if header and len(data) > 1:
            data.pop(0)

        for row in csv.reader(data):

            if len(row) != len(mapping):  # pragma: no cover
                raise DataError('csv row length does not match mapping')

            yield MarketData(dict(zip(mapping, row))).clean_dt(tz, close)

    # json format: yield each element as a MarketData object with clean dt
    elif format == 'json':

        # decode json data; force top-level to list
        data = json.loads(data)
        data = [data] if not isinstance(data, MutableSequence) else data

        for o in data:

            if not isinstance(o, MutableMapping):  # pragma: no cover
                raise DataError('json elements are not dicts')

            # replace keys
            o = dict(map(lambda x: (x[0], o.get(x[1], None)), mapping.items()))

            yield MarketData(o).clean_dt(tz, close)

    # raw format: yield the raw result
    elif format == 'raw':

        yield data


def get_yahoo_quote(symbol):
    '''
    Gets a delayed price quote for `symbol` from Yahoo! finance.

    :returns: `dict` type object with labeled price data
    :rtype: `MarketData`
    :param symbol: the ticker symbol of the instrument we want to price
    :type symbol: `str`
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
    Gets historical price data for `symbol` from Yahoo! finance.

    :returns: generator of `dict` type objects with labeled price data
    :rtype: `MarketData`
    :param symbol: the ticker symbol of the instrument we want to price
    :type symbol: `str`
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
    Gets a real-time price quote for `symbol` from CNBC.

    :returns: `dict` type object with labeled price data
    :rtype: `MarketData`
    :param symbol: the ticker symbol of the instrument we want to price
    :type symbol: `str`
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
    Gets a list of securities containing `symbol`.

    :returns: generator of `dict` type objects with labeled symbol data
    :rtype: `MarketData`
    :param symbol: the symbol or name fragment to find
    :type search: `str`
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

    :returns: time remaining until close or 'closed'
    :rtype: `str`
    '''

    return next(_get_data(
        '',
        _YAHOO_STATUS_US['source'],
        _YAHOO_STATUS_US['format'],
        pattern=_YAHOO_STATUS_US['pattern'],
    ))


def get_zipline_dp(bundle=None, calendar=None):
    '''
    Returns `zipline` data portal, used for symbol lookups and obtaining data.

    :rtype: `zipline.data.data_portal.DataPortal`
    :param bundle: optionally specify the `zipline` data bundle to use
    :param calendar: optionally specify the `zipline` calendar to use
    :type bundle: `zipline.data.bundles.core.BundleData`
    :type calendar: `zipline.utils.calendars.exchange_calendar_nyse` type
    '''

    z = _ZIPLINE_QUANDL_BUNDLE
    bundle = load(z['name']) if bundle is None else bundle
    calendar = get_calendar(z['cal']) if calendar is None else calendar

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
    Gets daily historical price data for `symbol` from a `zipline` data bundle.

    :returns: `field` data going back `bar_count` from `end_dt` for `symbol`
    :rtype: `pandas.Series` with `name` attribute set to
            `zipline.assets._assets.Equity`
    :param symbol: the ticker symbol of the instrument
    :param field: the desired OHLC field
    :param end_dt: the ending datetime of the series
    :param bar_count: the number of points in the timeseries
    :param frequency: the frequency of the timeseries (e.g. "1d" or "1m")
    :param bundle: optionally specify the `zipline` data bundle to use
    :param calendar: optionally specify the `zipline` calendar to use
    :type symbol: `str`
    :type field: `str`
    :type end_dt: `datetime.datetime` type object
    :type bar_count: `int`
    :type frequency: `str`
    :type bundle: `zipline.data.bundles.core.BundleData`
    :type calendar: `zipline.utils.calendars.exchange_calendar_nyse` type

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
    ).iloc[:, 0]

# -*- coding: utf-8 -*-

'''
classes
-------

custom `stockbot` classes
'''

################################################################################


import collections
import datetime as dt
from decimal import Decimal
import re

from dateutil.parser import parse
from dateutil.tz import tzlocal
import pytz


class MarketData(dict):
    '''
    `dict` subclass for storing market data; processes data based key, content
    '''

    decimal = False

    def __init__(self, *args, **kwargs):
        '''
        strips `MarketData` specific args and calls custom update
        :param decimal: turns use of `decimal.Decimal` on/off
        :type decimal: `bool` (default=False)
        '''

        self.decimal = kwargs.pop('decimal', self.decimal)
        self.update(*args, **kwargs)

    def __getitem__(self, k):
        return dict.__getitem__(self, k)

    def __setitem__(self, k, v):
        '''
        custom `__setitem__` converts date, time, datetime `str` to
        `dt.datetime` objects and all value fields that appear to be
        numerics to `int`, `float`, or `Decimal`

        :raises InvalidOperation: on bad decimal conversion
        '''

        # parse date, time, datetime value strings to dt objects
        if k in ['date', 'time', 'datetime'] and isinstance(v, str):
            v = parse(v)

        p = re.compile('^\-?(0|[1-9]\d*)(.\d+)([eE][\+\-]\d+)?$')

        # if value is a str and appears to be numeric, recast type
        if isinstance(v, str) and re.compile(p).search(v):

            if self.decimal:
                v = Decimal(v)

            elif '.' in v:
                v = float(v)

            else:
                v = int(v)

        dict.__setitem__(self, k, v)

    def __repr__(self):
        dict_repr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dict_repr)

    def update(self, *args, **kwargs):
        '''
        implements update by calling `dict.iteritems()`
        '''

        for k, v in dict(*args, **kwargs).iteritems():
            self[k] = v

    def clean_dt(self, tz=None, close=None):
        '''
        Combines 'date' and/or 'time' fields into 'datetime' and converts
        to `pytz.timezone('UTC')`

        :param tz: a `pytz` timezone label, defaults to 'America/New_York'
        :param close: market close time, defaults to `dt.datetime.now()` for tz
        :type tz: `str`
        :type close: `str`
        :raises ValueError: if `dateutil.parser.parse()` fails
        :raises TypeError: if `dt.datetime.combine()` fails
        :raises AttributeError: if `pytz.timezone().localize()` fails
        '''

        # parse tz if str
        if isinstance(tz, str):
            tz = pytz.timezone(tz)

        # set tz to America/New_York by default
        elif not tz:
            tz = pytz.timezone('America/New_York')

        # set close to now() in tz by default
        if not close:
            close = dt.datetime.now().replace(tzinfo=tzlocal()).astimezone(tz)

        # get date or default to today() in tz
        default = dt.datetime.today().replace(tzinfo=tzlocal()).astimezone(tz)
        date = self.get('date', default)

        # get time or default to close
        time = self.get('time', close)

        # get datetime or set to date + time
        d_t = self.get('datetime', dt.datetime.combine(date.date(), time.time()))

        # localize datetime to tz if naive and convert to UTC
        if not d_t.tzinfo:
            d_t = tz.localize(d_t)

        d_t = d_t.astimezone(pytz.timezone('UTC'))

        # remove date, time fields
        for k in ['date', 'time']:
            self.pop(k, None)

        # add datetime field
        self.setdefault('datetime', d_t)

        return self

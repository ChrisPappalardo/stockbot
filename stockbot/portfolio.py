# -*- coding: utf-8 -*-

'''
portfolio
---------

`stockbot` portfolio classes and functions
'''

################################################################################


from mock import Mock
from pandas import Timestamp
from numpy import isnan
from talib.abstract import ADX

from .sources import (
    get_zipline_dp,
    get_zipline_hist,
)


class Portfolio(object):
    '''
    Class for storing a collection of market instruments
    '''

    def __init__(self, *args, **kwargs):
        '''
        Looks up ticker symbols and stores `zipline` instrument objects

        `args` is one or more ticker symbol `str`s
        `kwargs` is one or more config key/value pairs

        example: Portfolio('AAPL', 'GOOG', calendar=get_calendar('NYSE'))
        '''

        # get config settings
        self.bundle = kwargs.pop('bundle', None)
        self.calendar = kwargs.pop('calendar', None)
        self.log = kwargs.pop('log', Mock())
        self.dataportal = kwargs.pop('dp',
                                     get_zipline_dp(self.bundle, self.calendar))

        # populate instruments
        self.portfolio = list()
        for s in args:
            i = self.dataportal.asset_finder.lookup_symbol(s, None)
            if i not in self.portfolio:
                self.portfolio.append(i)

    def __len__(self):
        return self.portfolio.__len__()

    def __str__(self):
        return self.portfolio.__str__()

    def __repr__(self):
        return self.portfolio.__repr__()

    def adx_rank(self, asof=None, bar_count=28):
        '''
        Returns a list of tuples ordered by descending ADX rating.

        `asof` is a `datetime`-like object with the desired day or `utcnow()`
        '''

        asof = Timestamp.utcnow() if asof is None else Timestamp(asof)
        result = dict()

        for i in self.portfolio:
            f = get_zipline_hist
            b = self.bundle
            c = self.calendar
            dp = self.dataportal
            input = {
                'high': f(i, 'high', asof, bar_count, '1d', b, c, dp),
                'low': f(i, 'low', asof, bar_count, '1d', b, c, dp),
                'close': f(i, 'close', asof, bar_count, '1d', b, c, dp),
            }
            # set ADX or log that we don't have data
            try:
                adx = ADX(input)[-1]
                if isnan(adx):
                    self.log.warn('adx for %s on %s is NaN' % (i.symbol, asof))
                else:
                    result[i] = ADX(input)[-1]
            except Exception as e:
                if 'inputs are all NaN' in e:
                    self.log.warn('NaN inputs for %s on %s' % (i.symbol, asof))
                else: # pragma: no cover
                    raise

        return sorted(result.items(), key=lambda t: t[1], reverse=True)

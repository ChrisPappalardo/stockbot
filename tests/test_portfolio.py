#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
test_portfolio
--------------

Tests `portfolio` module.
'''

import unittest

from logbook import Logger
from mock import (Mock, patch)
from numpy import (nan, random)
from pandas import (Series, Timestamp)
from zipline.errors import SymbolNotFound

from stockbot.portfolio import Portfolio


class TestPortfolio(unittest.TestCase):

    def setUp(self):
        pass

    def test_portfolio(self):
        '''
        ensure that basic methods and quandl instantiation work
        '''

        self.assertTrue(Portfolio('GE'))
        self.assertTrue(str(Portfolio('GE')))
        self.assertTrue(repr(Portfolio('GE')))
        self.assertEqual(len(Portfolio('THISSHOULDNOTBREAK')), 0)
        try:
            Portfolio('THISSHOULDBREAK', strict=True)
        except Exception as e:
            self.assertEqual(type(e), type(SymbolNotFound()))

    @patch('stockbot.portfolio.get_zipline_hist')
    def test_portfolio_adx_rank(self, mock_get_zipline_hist):
        '''
        test adx ranking using random numbers and partial and empty series
        '''

        a = Portfolio('GE', log=Logger('test'))

        b = Series([random.rand()*10 for i in range(0, 28)])
        mock_get_zipline_hist.return_value = b
        self.assertTrue(a.adx_rank(Timestamp.utcnow()))

        b = Series([random.rand()*10 for i in range(0, 27)])
        mock_get_zipline_hist.return_value = b
        self.assertEqual(a.adx_rank(Timestamp.utcnow()), [])

        b = Series([nan for i in range(0, 28)])
        mock_get_zipline_hist.return_value = b
        self.assertEqual(a.adx_rank(Timestamp.utcnow()), [])

    def tearDown(self):
        pass

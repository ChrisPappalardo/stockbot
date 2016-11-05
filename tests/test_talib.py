# -*- coding: utf-8 -*-

'''
test_talib
----------

tests `TA-lib` technical indicator third party package for accuracy
'''

import unittest

import pandas as pd
from numpy import isnan
from talib import abstract


OHLC_fields_talib = ['open', 'high', 'low', 'close']
OHLC_fields_adxdata = ['open', 'high', 'low', 'last']
tol_ADX_low = -1.0
tol_ADX_high = 1.0


class TestADX(unittest.TestCase):

    def setUp(self):
        self.data = pd.read_csv('tests/data/adx.csv')

    def test_ADX(self):
        talib_inpt = dict(zip(OHLC_fields_talib,
                              [self.data[f] for f in OHLC_fields_adxdata]))
        talib_calc = pd.Series(abstract.ADX(talib_inpt))
        talib_diff = talib_calc - self.data['adx']
        talib_test = lambda x: isnan(x) | (x >= tol_ADX_low and x <= tol_ADX_high)

        # every diff between talib ADX and test ADX is NaN or within tolerances
        self.assertTrue(all(talib_test(x) for x in talib_diff))

    def tearDown(self):
        pass

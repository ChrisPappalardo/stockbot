# -*- coding: utf-8 -*-

'''
test_talib
----------

tests `TA-lib` technical indicator third party package for accuracy
'''

import unittest

import pandas as pd
from numpy import isnan
from talib.abstract import (
    TRANGE,
    PLUS_DI,
    MINUS_DI,
    ADX,
)

from core import remap


class TestTAlib(unittest.TestCase):

    def setUp(self):
        self.adxdata = pd.read_csv('tests/data/adx.csv')

    def test_TR(self):
        '''
        talib TR and test TR differences are NaN or within tolerances
        '''

        field_map = {
            'last': 'close',
        }
        input = remap(field_map, self.adxdata)

        calc = pd.Series(TRANGE(input))
        diff = calc - input['tr1']
        test = lambda x: isnan(x) | (x >= -1.0 and x <= 1.0)
        self.assertTrue(all(test(x) for x in diff))

    def test_DI(self):
        '''
        talib DI and test DI differences are NaN or within tolerances
        '''

        field_map = {
            'last': 'close',
        }
        input = remap(field_map, self.adxdata)

        fcn_map = {
            'pdi': PLUS_DI,
            'mdi': MINUS_DI,
        }

        for (k, f) in fcn_map.items():
            calc = pd.Series(f(input))
            diff = calc - input[k]
            test = lambda x: isnan(x) | (x >= -1.0 and x <= 1.0)
            self.assertTrue(all(test(x) for x in diff))

    def test_ADX(self):
        '''
        talib ADX and test ADX differences are NaN or within tolerances
        '''

        field_map = {
            'last': 'close',
        }
        input = remap(field_map, self.adxdata)

        calc = pd.Series(ADX(input))
        diff = calc - input['adx']
        test = lambda x: isnan(x) | (x >= -1.0 and x <= 1.0)
        self.assertTrue(all(test(x) for x in diff))

    def tearDown(self):
        pass

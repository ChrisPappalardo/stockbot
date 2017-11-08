# -*- coding: utf-8 -*-

'''
test_stockbot
-------------

Tests `stockbot` package import.
'''

import unittest
import stockbot


class TestStockbot(unittest.TestCase):

    def setUp(self):
        pass

    def test_stockbot(self):
        assert(stockbot.__name__ == 'stockbot')

    def tearDown(self):
        pass

# -*- coding: utf-8 -*-

'''
test_algo
---------

Tests `stockbot` algo package and dependencies.
'''

import unittest

from pandas import (Timestamp, DateOffset, DataFrame)
from zipline.utils.calendars import get_calendar
from zipline.utils.run_algo import run_algorithm


def initialize(context):
    pass


def handle_data(context, data):
    pass


class TestCore(unittest.TestCase):

    def setUp(self):
        pass

    def test_zipline(self):
        '''
        a do-nothing algo to test zipline through latest close
        '''

        end = get_calendar('NYSE').previous_close(Timestamp.utcnow())
        start = get_calendar('NYSE').previous_close(end - DateOffset(years=1))
        capital_base = float('1.0e5')

        res = run_algorithm(
            start=start,
            end=end,
            initialize=initialize,
            capital_base=capital_base,
        )

        self.assertTrue(start in res.index and end in res.index)

    def tearDown(self):
        pass

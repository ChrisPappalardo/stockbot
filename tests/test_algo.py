# -*- coding: utf-8 -*-

'''
test_algo
---------

Tests `stockbot` algo package and dependencies.
'''

import unittest
from mock import Mock

from pandas import (Timestamp, DateOffset, DataFrame)
from zipline.assets import Equity
from zipline.utils.calendars import get_calendar
from zipline.utils.run_algo import run_algorithm

from stockbot.algo.core import init


class TestCore(unittest.TestCase):

    def setUp(self):
        pass

    def test_zipline(self):
        '''
        a do-nothing algo to test zipline through latest close
        '''

        def initialize(context):
            pass

        end = get_calendar('NYSE').previous_close(Timestamp.utcnow())
        start = get_calendar('NYSE').previous_close(end - DateOffset(years=1))

        res = run_algorithm(
            start=start,
            end=end,
            initialize=initialize,
            capital_base=float('1.0e5'),
        )

        self.assertTrue(start in res.index and end in res.index)

    def test_algo_init(self):
        '''
        test init symbol checking
        '''

        def initialize(context):
            symbols = ['AAPL', 'GE', 'JNJ', 'THEBADONE']
            return init(context, 'test', symbols=symbols)

        def handle_data(context, data, s=self):
            s.context = context

        end = get_calendar('NYSE').previous_close(Timestamp.utcnow())
        start = get_calendar('NYSE').previous_close(end - DateOffset(days=1))

        res = run_algorithm(
            start=start,
            end=end,
            initialize=initialize,
            handle_data=handle_data,
            capital_base=float('1.0e5'),
        )

        self.assertListEqual(
            ['AAPL', 'GE', 'JNJ'],
            [s.symbol for s in self.context.sbot['symbols']],
        )
        self.assertEqual(
            self.context.sbot['capital_ppt'],
            1.0 / len(self.context.sbot['symbols']),
        )

    def tearDown(self):
        pass

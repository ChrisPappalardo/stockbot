# -*- coding: utf-8 -*-

'''
test_core
---------

Tests `stockbot` core package.
'''

import unittest
from mock import (patch, Mock)

from stockbot.core import (
    get_sp500_list,
)


class TestCore(unittest.TestCase):

    def setUp(self):
        pass

    @patch('stockbot.core.get')
    def test_get_sp500_list(self, mock_get):
        '''
        returns sp500 list from saved wikipedia page 11/7/16
        '''

        a = Mock()
        with open('tests/data/sp500wikilist.html', 'r') as f:
            a.content = f.read()
        mock_get.return_value = a
        a = get_sp500_list(False)
        self.assertEqual(len(a), 505)
        self.assertEqual(a[45]['Ticker symbol'], 'AAPL')

    def tearDown(self):
        pass

# -*- coding: utf-8 -*-

'''
test_sources
------------

Tests `stockbot.sources` module.
'''

import datetime as dt
from mock import (patch, Mock)
import unittest

import pandas as pd
import pytz

from stockbot.sources import (get_yahoo_quote,
                              get_yahoo_hist,
                              get_cnbc_quote,
                              get_symbol,
                              get_status_US)


class TestSources(unittest.TestCase):

    def setUp(self):
        pass

    @patch('stockbot.sources.urlopen')
    def test_get_yahoo_quote(self, mock_urlopen):
        _in = u'"SPY",188.01,"9/28/2015","4:23pm",-4.84,191.78,191.91,187.64,178515871\n'
        out_labels = ['symbol', 'last', 'change', 'open', 'high', 'low', 'volume', 'datetime']
        out_values = ['SPY', '188.01', '-4.84', '191.78', '191.91', '187.64', '178515871',
                      dt.datetime(2015, 9, 28, 20, 23, 00, tzinfo=pytz.timezone('UTC'))]
        a = Mock()
        a.readlines.side_effect = [[_in]]
        mock_urlopen.return_value = a
        b = get_yahoo_quote('')
        c = pd.Series(out_values, index=out_labels)
        assert(b.equals(c))

    def tearDown(self):
        pass

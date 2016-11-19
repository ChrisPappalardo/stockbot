# -*- coding: utf-8 -*-

'''
test_sources
------------

tests `stockbot.sources` module
'''

import datetime as dt
import unittest

from mock import (patch, Mock)
from pandas import (Series, Timestamp)
import pytz
from six import StringIO
from zipline.data.data_portal import DataPortal

from stockbot.sources import (
    DataError,
    _get_data,
    get_yahoo_quote,
    get_yahoo_hist,
    get_cnbc_quote,
    get_symbol,
    get_status_US,
    get_zipline_dp,
    get_zipline_hist,
)


class TestSources(unittest.TestCase):

    def setUp(self):
        pass

    def test_data_error(self):
        try:
            raise DataError('test')
        except DataError as e:
            self.assertEqual(e.value, 'test')
            self.assertEqual(str(e), 'test')

    @patch('stockbot.sources.urlopen')
    def test_get_yahoo_quote(self, mock_urlopen):
        _in = '"SPY",188.01,"9/28/2015","4:23pm",-4.84,191.78,191.91,187.64,178515871\n'
        out_labels = ['symbol', 'last', 'change', 'open', 'high', 'low', 'volume', 'datetime']
        out_values = [
            'SPY', 188.01, -4.84, 191.78, 191.91, 187.64, 178515871,
            dt.datetime(2015, 9, 28, 20, 23, 00, tzinfo=pytz.timezone('UTC'))
        ]
        a = Mock()
        a.readlines.side_effect = [StringIO(_in).readlines()]
        mock_urlopen.return_value = a
        b = dict(get_yahoo_quote(''))
        c = dict(zip(out_labels, out_values))
        self.assertDictEqual(b, c)

    @patch('stockbot.sources.urlopen')
    def test_get_yahoo_hist(self, mock_urlopen):
        _in = 'Date,Open,High,Low,Close,Volume,Adj Close\n2015-09-30,190.369995,191.830002,189.440002,191.589996,152593200,191.589996\n'
        out_labels = ['open', 'high', 'low', 'close', 'volume', 'last', 'datetime']
        out_values = [
            190.369995, 191.830002, 189.440002, 191.589996, 152593200, 191.589996,
            dt.datetime(2015, 9, 30, 20, 00, tzinfo=pytz.timezone('UTC'))
        ]
        a = Mock()
        a.readlines.side_effect = [StringIO(_in).readlines()]
        mock_urlopen.return_value = a
        b = dict(next(get_yahoo_hist('')))
        c = dict(zip(out_labels, out_values))
        self.assertDictEqual(b, c)

    @patch('stockbot.sources.urlopen')
    def test_get_cnbc_quote(self, mock_urlopen):
        _in = 'var quoteDataObj = [{"symbol":"SPY","symbolType":"symbol","code":0,"name":"SPDR S\\u0026P 500 ETF Trust","shortName":"SPY","last":"191.72","exchange":"NYSE Arca","source":"NYSE ARCA Real-Time Stock Prices","open":"192.08","high":"192.49","low":"189.82","change":"0.09","currencyCode":"USD","timeZone":"EDT","volume":"95412152","provider":"CNBC QUOTE CACHE","altSymbol":"SPY","curmktstatus":"REG_MKT","realTime":"true","assetType":"STOCK","noStreaming":"false","encodedSymbol":"SPY"}]'
        out_labels = ['symbol', 'last', 'change', 'open', 'high', 'low', 'volume', 'datetime']
        out_values = ['SPY', 191.72, 0.09, 192.08, 192.49, 189.82, 95412152]
        a = Mock()
        a.readlines.side_effect = [StringIO(_in).readlines()]
        mock_urlopen.return_value = a
        b = dict(next(get_cnbc_quote('')))
        c = dict(zip(out_labels, out_values))
        c['datetime'] = b['datetime']
        self.assertDictEqual(b, c)

    @patch('stockbot.sources.urlopen')
    def test_get_symbol(self, mock_urlopen):
        _in = '{"ResultSet":{"Query":"SPY","Result":[{"symbol":"SPY","name":"SPDR S&P 500 ETF","exch":"PCX","type":"E","exchDisp":"NYSEArca","typeDisp":"ETF"}]}}'
        out_labels = ['symbol', 'name', 'exchange', 'type']
        out_values = ['SPY', 'SPDR S&P 500 ETF', 'PCX', 'ETF']
        a = Mock()
        a.readlines.side_effect = [StringIO(_in).readlines()]
        mock_urlopen.return_value = a
        b = dict(next(get_symbol('')))
        c = dict(zip(out_labels, out_values))
        c['datetime'] = b['datetime']
        self.assertDictEqual(b, c)

    @patch('stockbot.sources.urlopen')
    def test_get_status_US(self, mock_urlopen):
        _in = '<span class="Va(m)" data-reactid=".1fyl5igkzba.0.$0.0.1.3.0.0.0.1.0.0.1">U.S. Markets closed</span>'
        a = Mock()
        a.readlines.side_effect = [StringIO(_in).readlines()]
        mock_urlopen.return_value = a
        b = get_status_US()
        self.assertEqual(b, 'closed')

    def test_zipline_dp(self):
        self.assertTrue(isinstance(get_zipline_dp(), DataPortal))

    def test_zipline_hist(self):
        t = Timestamp.utcnow()
        self.assertTrue(isinstance(get_zipline_hist('GE', 'close', t), Series))

    def tearDown(self):
        pass

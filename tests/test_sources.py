# -*- coding: utf-8 -*-

'''
test_sources
------------

tests `stockbot.sources` module
'''

import datetime as dt
import sys
import unittest
if sys.version_info > (3, 0):
    from io import StringIO
else:
    from StringIO import StringIO

from mock import (patch, Mock)
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
        out_values = [
            'SPY', 188.01, -4.84, 191.78, 191.91, 187.64, 178515871,
            dt.datetime(2015, 9, 28, 20, 23, 00, tzinfo=pytz.timezone('UTC'))
        ]
        a = Mock()
        a.readlines.side_effect = [StringIO(_in).readlines()]
        mock_urlopen.return_value = a
        b = get_yahoo_quote('')
        c = dict(zip(out_labels, out_values))
        self.assertEqual(b, c)

    @patch('stockbot.sources.urlopen')
    def test_get_yahoo_hist(self, mock_urlopen):
        _in = u'Date,Open,High,Low,Close,Volume,Adj Close\n2015-09-30,190.369995,191.830002,189.440002,191.589996,152593200,191.589996\n'
        out_labels = ['open', 'high', 'low', 'close', 'volume', 'last', 'datetime']
        out_values = [
            190.369995, 191.830002, 189.440002, 191.589996, 152593200, 191.589996,
            dt.datetime(2015, 9, 30, 20, 00, tzinfo=pytz.timezone('UTC'))
        ]
        a = Mock()
        a.readlines.side_effect = [StringIO(_in).readlines()]
        mock_urlopen.return_value = a
        b = next(get_yahoo_hist(''))
        c = dict(zip(out_labels, out_values))
        self.assertEqual(b, c)
        '''
    @patch('stockbot.sources.urlopen')
    def test_get_cnbc_quote(self, mock_urlopen):
        _in = u'var quoteDataObj = [{"symbol":"SPY","symbolType":"symbol","code":0,"name":"SPDR S\\u0026P 500 ETF Trust","shortName":"SPY","last":"191.72","exchange":"NYSE Arca","source":"NYSE ARCA Real-Time Stock Prices","open":"192.08","high":"192.49","low":"189.82","change":"0.09","currencyCode":"USD","timeZone":"EDT","volume":"95412152","provider":"CNBC QUOTE CACHE","altSymbol":"SPY","curmktstatus":"REG_MKT","realTime":"true","assetType":"STOCK","noStreaming":"false","encodedSymbol":"SPY"}]'
        out_labels = ['symbol', 'last', 'change', 'open', 'high', 'low', 'volume', 'datetime']
        out_values = [
            'SPY', '191.72', '0.09', '192.08', '192.49', '189.82', '95412152',
            dt.datetime(2015, 9, 28, 20, 23, 00, tzinfo=pytz.timezone('UTC'))
        ]
        a = Mock()
        a.readlines.side_effect = [[_in]]
        mock_urlopen.return_value = a
        b = get_yahoo_quote('')
        c = pd.Series(out_values, index=out_labels)
        assert(b.equals(c))

    @patch('stockbot.sources.urlopen')
    def test_get_cnbc_quote(self, mock_urlopen):
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

    @patch('stockbot.sources.urlopen')
    def test_get_cnbc_quote(self, mock_urlopen):
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
        '''

    def tearDown(self):
        pass

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
from zipline.data.data_portal import DataPortal

from stockbot.sources import (
    DataError,
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
        self.a = Mock()

    def test_data_error(self):
        try:
            raise DataError('test')
        except DataError as e:
            self.assertEqual(e.value, 'test')
            self.assertEqual(str(e), 'test')

    @patch('stockbot.sources.get')
    def test_get_yahoo_quote(self, mock_get):
        _in = '"SPY",188.01,"9/28/2015","4:23pm",-4.84,191.78,191.91,187.64,178515871\n'
        out_labels = ['symbol', 'last', 'change', 'open', 'high', 'low', 'volume', 'datetime']
        out_values = [
            'SPY', 188.01, -4.84, 191.78, 191.91, 187.64, 178515871,
            dt.datetime(2015, 9, 28, 20, 23, 00, tzinfo=pytz.timezone('UTC'))
        ]
        self.a.text = _in
        mock_get.return_value = self.a
        b = dict(get_yahoo_quote(''))
        c = dict(zip(out_labels, out_values))
        self.assertDictEqual(b, c)

    @patch('stockbot.sources.get')
    def test_get_yahoo_hist(self, mock_get):
        _in = 'Date,Open,High,Low,Close,Adj Close,Volume\n2015-09-30,190.369995,191.830002,189.440002,191.589996,191.589996,152593200\n'
        out_labels = ['open', 'high', 'low', 'close', 'volume', 'last', 'datetime']
        out_values = [
            190.369995, 191.830002, 189.440002, 191.589996, 152593200, 191.589996,
            dt.datetime(2015, 9, 30, 20, 00, tzinfo=pytz.timezone('UTC'))
        ]
        self.a.text = _in
        self.a.cookies = dict()
        mock_get.return_value = self.a
        b = dict(next(get_yahoo_hist('')))
        c = dict(zip(out_labels, out_values))
        self.assertDictEqual(b, c)

    @patch('stockbot.sources.get')
    def test_get_cnbc_quote(self, mock_get):
        _in = '{"QuickQuoteResult":{"QuickQuote":{"change_pct":"1.01","last":"262.87","curmktstatus":"POST_MKT","change":"2.64","issue_id":"258981","reg_last_time":"2017-11-28T18:30:00.000-0500","timeZone":"EST","last_time":"2017-11-28T18:30:00.000-0500","mappedSymbol":{"xsi:nil":"true"},"realTime":"true","providerSymbol":{"xsi:nil":"true"},"open":"260.76","issuer_id":"165357","quoteDesc":{},"assetType":"STOCK","name":"SPDR S&P 500 ETF Trust","cachedTime":"Tue Nov 28 18:38:33 EST 2017","streamable":"1","responseTime":"Tue Nov 28 18:38:33 EST 2017","exchange":"NYSE Arca","currencyCode":"USD","symbol":"SPY","prev_prev_closing":"260.36","assetSubType":"Exchange Traded Fund","FundamentalData":{"ROETTM":"-0.45815","yragopricechangepct":"18.666481","yrhidate":"2017-11-28","GROSMGNTTM":"98.61016","DEBTEQTYQ":"0.00000","beta":"1.01537","NETPROFTTM":"-19.78282","yragoprice":"221.52000","mktcapView":"252972.93M","yrlodate":"2016-12-01","dividendyield":"0.01818275","mktcap":"252972992375.0244140625","pcttendayvol":"1.709","tendayavgvol":"57830632.00","dividend":"4.7797","MPreviousClose":"260.23000","PDYTDPCHG":"16.41838","eps":"-1.45626","pe":"-180.51035","sharesoutView":"962.35M","sharesout":"962350200","revenuettmView":"4013.44M","yrhiprice":"262.9","revenuettm":"4013438000","TTMEBITD":"3839.47300","yrloprice":"219.15","yragopricechange":"41.34999"},"countryCode":"US","provider":"CNBC QUOTE CACHE","code":"0","onAirName":"SPDR S&P 500 ETF","source":"Last Trade from NYSE Arca, Volume from CTA","cacheServed":"false","altName":"SPDR S&P 500 ETF Trust","altSymbol":"SPY","todays_closing":"262.87","volume":"81937369","previous_day_closing":"260.23","high":"262.90","shortName":"SPY","low":"260.655","comments":"Composite","last_time_msec":"1511911800000","symbolType":"symbol","fullVolume":"98831499"},"xmlns:xsi":"","xmlns":""}}'
        out_labels = ['symbol', 'last', 'change', 'open', 'high', 'low', 'volume', 'datetime']
        out_values = ['SPY', 262.87, 2.64, 260.76, 262.9, 260.655, 81937369]
        self.a.text = _in
        mock_get.return_value = self.a
        b = dict(next(get_cnbc_quote('')))
        c = dict(zip(out_labels, out_values))
        c['datetime'] = b['datetime']
        self.assertDictEqual(b, c)

    @patch('stockbot.sources.get')
    def test_get_symbol(self, mock_get):
        _in = '{"ResultSet":{"Query":"SPY","Result":[{"symbol":"SPY","name":"SPDR S&P 500 ETF","exch":"PCX","type":"E","exchDisp":"NYSEArca","typeDisp":"ETF"}]}}'
        out_labels = ['symbol', 'name', 'exchange', 'type']
        out_values = ['SPY', 'SPDR S&P 500 ETF', 'PCX', 'ETF']
        self.a.text = _in
        mock_get.return_value = self.a
        b = dict(next(get_symbol('')))
        c = dict(zip(out_labels, out_values))
        c['datetime'] = b['datetime']
        self.assertDictEqual(b, c)

    @patch('stockbot.sources.get')
    def test_get_status_US(self, mock_get):
        _in = '<span class="Va(m)" data-reactid=".1fyl5igkzba.0.$0.0.1.3.0.0.0.1.0.0.1">U.S. Markets closed</span>'
        self.a.text = _in
        mock_get.return_value = self.a
        b = get_status_US()
        self.assertEqual(b, 'closed')

    def test_zipline_dp(self):
        self.assertTrue(isinstance(get_zipline_dp(), DataPortal))

    def test_zipline_hist(self):
        t = Timestamp.utcnow()
        self.assertTrue(isinstance(get_zipline_hist('GE', 'close', t), Series))

    def tearDown(self):
        pass

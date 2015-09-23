#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_stockbot
----------------------------------

Tests for `stockbot` module.
"""

import unittest

from stockbot import stockbot


class TestStockbot(unittest.TestCase):

    def setUp(self):
        pass

    def test_foo(self):
        assert(stockbot.foo())

    def tearDown(self):
        pass

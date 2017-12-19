# -*- coding: utf-8 -*-

'''
adx_sar_so
----------

stockbot sp500 parabolic sar and oscillator trading system using adx
'''

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from logbook import Logger

from stockbot.algo.core import (
    init,
    adx_rank,
    trade_sar,
    trade_so,
)
from stockbot.core import get_sp500_list


def initialize(context):
    return init(
        context,
        name='adx_sar_so',
        symbols=get_sp500_list(),
        capital_ppt=1.0/(5.0 + 5.0),
        fillna='bfill',
        fillna_limit=0.34,
        log=Logger('Stockbot'),
        top_rank=5,
        bot_rank=5,
        di_window=14,
        accel=0.02,
        accel_max=0.2,
        so_window=14,
        top=[],
        bot=[],
    )


def handle_data(context, data):
    # increment counter and log datetime
    context.i += 1
    context.sbot['log'].info('processing %s' % context.get_datetime())

    # rank S&P500 stocks for the current iteration
    adx_rank(
        context,
        data,
        symbols=context.sbot['symbols'],
        top_rank=context.sbot['top_rank'],
        bot_rank=context.sbot['bot_rank'],
        di_window=context.sbot['di_window'],
    )

    # trade trending S&P500 stocks using parabolic stop-and-reverse points
    trade_sar(
        context,
        data,
        t_symbols=[s for (s, adx) in context.sbot['top']],
        accel=context.sbot['accel'],
        accel_max=context.sbot['accel_max'],
    )

    # trade oscillating S&P500 stocks using stochastic oscillators
    trade_so(
        context,
        data,
        o_symbols=[s for (s, adx) in context.sbot['bot']],
        so_window=context.sbot['so_window'],
    )

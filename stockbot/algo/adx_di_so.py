# -*- coding: utf-8 -*-

'''
adx_di_so
---------

stockbot S&P500 directional movement and oscillator trading system using adx
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
    trade_di,
    trade_so,
)
from stockbot.core import get_sp500_list


def initialize(context):
    return init(
        context,
        name='adx_di_so',
        symbols=get_sp500_list(),
        capital_ppt=1.0/(5.0 + 5.0),
        fillna='bfill',
        fillna_limit=0.34,
        log=Logger('Stockbot'),
        top_rank=5,
        bot_rank=5,
        di_window=14,
        so_window=14,
        top=[],
        bot=[],
        rank_every=7,
    )


def handle_data(context, data):
    # increment counter and log datetime
    context.i += 1
    context.sbot['log'].info('processing %s' % context.get_datetime())

    # rank S&P500 stocks if this is a rank iteration
    # subtract 1 from i so first iteration produces a ranking
    if (context.i - 1) / context['rank_every'] % 1 == 0.0:
        adx_rank(
            context,
            data,
            symbols=context.sbot['symbols'],
            top_rank=context.sbot['top_rank'],
            bot_rank=context.sbot['bot_rank'],
            di_window=context.sbot['di_window'],
        )

    # trade trending S&P500 stocks using the DI system
    trade_di(
        context,
        data,
        t_symbols=[s for (s, adx) in context.sbot['top']],
        di_window=context.sbot['di_window'],
    )

    # trade oscillating S&P500 stocks using the SO system
    trade_so(
        context,
        data,
        o_symbols=[s for (s, adx) in context.sbot['bot']],
        so_window=context.sbot['so_window'],
    )

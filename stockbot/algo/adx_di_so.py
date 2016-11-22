# -*- coding: utf-8 -*-

'''
adx_di_so
---------

stockbot S&P500 directional movement and oscillator trading system using adx
'''

###############################################################################


from logbook import Logger

from stockbot.algo.core import (
    adx_init,
    trade_di,
    trade_so,
)
from stockbot.core import get_sp500_list


def initialize(context):
    return adx_init(
        context,
        name='adx_di_so',
        top_rank=5,
        bot_rank=5,
        di_window=14,
        symbols=get_sp500_list(),
        log=Logger('Stockbot'),
    )


def handle_data(context, data):
    # increment counter and log datetime
    context.i += 1
    context.adx['log'].info('processing %s' % context.get_datetime())

    # trade trending S&P500 stocks using the DI system
    trade_di(
        context,
        data,
        window=context.adx['di_window'],
        portfolio=[i for (i, adx) in context.adx['top']],
        capital_ppi=1.0/(len(context.adx['top'])+len(context.adx['bot'])),
        log=context.adx['log'],
    )

    # trade oscillating S&P500 stocks using the SO system
    trade_so(
        context,
        data,
        window=context.adx['di_window'],
        portfolio=[i for (i, adx) in context.adx['bot']],
        capital_ppi=1.0/(len(context.adx['top'])+len(context.adx['bot'])),
        log=context.adx['log'],
    )

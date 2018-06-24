# -*- coding: utf-8 -*-

'''
ml_rank_ls
----------

stockbot sp500 long/short rank trading system using machine learning
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
    model_rank,
    trade_top_bot,
)
from stockbot.core import get_sp500_list


class Initialize(object):
    '''
    class-based initialization for ml_rank_ls enables injectable config
    '''

    config = {
        'name': 'ml_rank_ls',
        'symbols': get_sp500_list(),
        'capital_ppt': 1.0 / (5.0 + 5.0),
        'fillna': 'bfill',
        'fillna_limit': 0.34,
        'log': Logger('Stockbot'),
        'top_rank': 5,
        'bot_rank': 5,
        'window': 14,
        'windows': 2,
        'accel': 0.02,
        'accel_max': 0.2,
        'rank': [],
        'top': [],
        'bot': [],
        'model': None,
        'rank_every': 14,
    }

    def __init__(self, context):
        return init(context, **self.config)


initialize = Initialize


def handle_data(context, data):
    '''
    calls model.rank on rank_every and buys/sells top_rank, bot_rank
    '''

    context.i += 1
    context.sbot['log'].info('processing %s' % context.get_datetime())

    # subtract 1 from i so first iteration produces a ranking
    if (context.i - 1) / context.sbot['rank_every'] % 1 == 0.0:
        model_rank(
            context,
            data,
            model=context.sbot['model'],
            symbols=context.sbot['symbols'],
            top_rank=context.sbot['top_rank'],
            bot_rank=context.sbot['bot_rank'],
            window=context.sbot['window'],
            windows=context.sbot['windows'],
            accel=context.sbot['accel'],
            accel_max=context.sbot['accel_max'],
        )

        trade_top_bot(
            context,
            symbols=[s for (s, rank) in context.sbot['rank']],
            top=[s for (s, rank) in context.sbot['top']],
            bot=[s for (s, rank) in context.sbot['bot']],
        )

# -*- coding: utf-8 -*-

'''
adx_di
------

directional movement indicator system for top ADX stocks
'''

################################################################################


import logbook
from talib.abstract import ADX
from zipline.api import (
    order_target,
    record,
    symbol,
)
from zipline.errors import SymbolNotFound

from stockbot.core import get_sp500_list


def initialize(context):
    # reset iteration cursor
    context.i = 0

    # set stock population, TI window, rank levels
    context.sym = list()
    context.window = 14
    context.top_rank = 5
    context.bot_rank = 5

    for s in get_sp500_list():
        try:
            context.sym.append(symbol(s))
        except SymbolNotFound:
            pass

    # create stockbot log and add config line
    context.log = logbook.Logger('Stockbot')
    m = 'Stockbot ADX/DI program initialized with %s stocks'
    context.log.info(m % len(context.sym))


def handle_data(context, data):
    # Skip first window*2 days to get the ADX/DI window
    context.i += 1
    if context.i < context.window * 2:
        return

    # calculate ADX for all stocks
    adx = dict()
    for s in context.sym:
        input = {
            'high': data.history(s, 'high', context.window * 2, '1d'),
            'low': data.history(s, 'low', context.window * 2, '1d'),
            'close': data.history(s, 'close', context.window * 2, '1d'),
        }
        try:
            adx[s.symbol] = ADX(input)[-1]
        except Exception as e:
            if 'inputs are all NaN' not in e: raise

    # store top and bottom ranks
    key = lambda t: t[1]
    adx_sort = sorted(adx.items(), key=key, reverse=True)
    context.log.info('%s %s' % (adx_sort[:5], adx_sort[-5:]))

    # Compute averages
    # history() has to be called with the same params
    # from above and returns a pandas dataframe.
#    short_mavg = history(100, '1d', 'price').mean()
#    long_mavg = history(300, '1d', 'price').mean()

#    sym = symbol('AAPL')

    # Trading logic
#    if short_mavg[sym] > long_mavg[sym]:
        # order_target orders as many shares as needed to
        # achieve the desired number of shares.
#        order_target(sym, 100)
#    elif short_mavg[sym] < long_mavg[sym]:
#        order_target(sym, 0)

    # Save values for later inspection
#    record(AAPL=data[sym].price,
#           short_mavg=short_mavg[sym],
#           long_mavg=long_mavg[sym])

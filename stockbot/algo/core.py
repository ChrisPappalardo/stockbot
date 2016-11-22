# -*- coding: utf-8 -*-

'''
algo.core
---------

core functions and objects for stockbot trading algorithms
'''

###############################################################################


from mock import Mock
from talib.abstract import (
    PLUS_DI,
    MINUS_DI,
    STOCH,
)
from zipline.api import (
    order_percent,
)

import stockbot.portfolio as sbp


def adx_init(context,
             name='adx',
             top_rank=5,
             bot_rank=5,
             di_window=14,
             symbols=None,
             log=None):
    '''
    zipline trading algorithm initialization that ranks portfolio using ADX
    and then stores the top trending and oscillating instruments in the context

    :param context: the context for the trading system
    :param name: the name of the trading system for log entries
    :param top_rank: the number of trending instruments to store
    :param bot_rank: the number of oscillating instruments to store
    :param di_window: the base DI window period (ADX window is * 2)
    :param symbols: the symbols to inlcude in portfolio
    :param log: log to use for adx ranking
    :type context: `zipline.algorithm.TradingAlgorithm`
    :type name: `str`
    :type top_rank: `int`
    :type bot_rank: `int`
    :type di_window: `int`
    :type symbols: `list` of `str`
    :type log: `logbook.Logger`
    '''

    # create iteration cursor
    context.i = 0

    # store config
    context.adx = {
        'name': name,
        'top_rank': top_rank,
        'bot_rank': bot_rank,
        'di_window': di_window,
        'symbols': list() if symbols is None else symbols,
        'log': Mock() if log is None else log,
    }
    c = context.adx

    # create stock portfolio and get ADX ranking for end_session date
    try:
        c['port'] = sbp.Portfolio(*c['symbols'], log=c['log'])
        e = context.sim_params.end_session
        c['rank'] = c['port'].adx_rank(e, c['di_window']*2)
        c['top'] = c['rank'][:c['top_rank']]
        c['bot'] = c['rank'][-c['bot_rank']:]
    except Exception as e:
        c['log'].error('an error occurred in %s: %s' % (c['name'], str(e)))
        raise

    # create log messages
    v = (
        c['name'],
        len(c['port']),
        context.sim_params.start_session,
        context.sim_params.end_session,
    )
    c['log'].info('trading %s with %s instruments from %s to %s' % v)
    c['log'].info('top adx symbols: %s' % [s.symbol for (s, adx) in c['top']])
    c['log'].info('bot adx symbols: %s' % [s.symbol for (s, adx) in c['bot']])


def trade_di(context,
             data,
             window,
             portfolio,
             capital_ppi,
             log):
    '''
    zipline trading algorithm that uses the Directional Indicator system for
    trending instruments

    :param context: the context for the trading system
    :param data: data for the trading system
    :param window: the DI window period
    :param portfolio: instruments to trade
    :param capital_ppi: capital % per instrument
    :param log: log to use for trading system
    :type context: `zipline.algorithm.TradingAlgorithm`
    :type data: `zipline.data.data_portal.DataPortal`
    :type window: `int`
    :type portfolio: `list` of `zipline.assets._assets` objects (e.g. `Equity`)
    :type capital_ppi: `Decimal`
    :type log: `logbook.Logger` or `Mock` object

    expects the following in `context`:

    :param i: iteration counter
    :param portfolio: current positions
    :type i: `int`
    :type portfolio: `zipline.protocol.Portfolio`
    '''

    # ensure we have enough history
    if context.i < window + 1:
        return

    # step through each instrument
    for i in portfolio:

        # calculate plus and minus directional movement indicators
        input = {
            'high': data.history(i, 'high', window + 1, '1d'),
            'low': data.history(i, 'low', window + 1, '1d'),
            'close': data.history(i, 'close', window + 1, '1d'),
        }
        (plus_di, minus_di) = (PLUS_DI(input), MINUS_DI(input))

        p = context.portfolio.positions
        v = (i.symbol, plus_di[-1], minus_di[-1])

        # go long if plus directional movement is greater
        if plus_di[-1] >= minus_di[-1]:
            if (i not in p) or (i in p and p[i].amount <= 0):
                log.info('long %s (+DI %s >= -DI %s)' % v)
                order_percent(i, capital_ppi)

        # go short if minus directional movement is greater
        else:
            if (i not in p) or (i in p and p[i].amount >= 0):
                log.info('short %s (+DI %s < -DI %s)' % v)
                order_percent(i, -capital_ppi)


def trade_so(context,
             data,
             window,
             portfolio,
             capital_ppi,
             log):
    '''
    zipline trading algorithm that uses the Stochastic Oscillator system for
    trending instruments

    :param context: the context for the trading system
    :param data: data for the trading system
    :param window: the SO window period
    :param portfolio: instruments to trade
    :param capital_ppi: capital % per instrument
    :param log: log to use for trading system
    :type context: `zipline.algorithm.TradingAlgorithm`
    :type data: `zipline.data.data_portal.DataPortal`
    :type window: `int`
    :type portfolio: `list` of `zipline.assets._assets` objects (e.g. `Equity`)
    :type capital_ppi: `Decimal`
    :type log: `logbook.Logger` or `Mock` object

    expects the following in `context`:

    :param i: iteration counter
    :param portfolio: current positions
    :type i: `int`
    :type portfolio: `zipline.protocol.Portfolio`
    '''

    # ensure we have enough history
    if context.i < window + 4:
        return

    # step through each instrument
    for i in portfolio:

        # calculate plus and minus directional movement indicators
        input = {
            'high': data.history(i, 'high', window + 4, '1d'),
            'low': data.history(i, 'low', window + 4, '1d'),
            'close': data.history(i, 'close', window + 4, '1d'),
        }
        STOCH.set_parameters({'fastk_period': window})
        (so_k, so_d) = STOCH(input)

        p = context.portfolio.positions
        v = (i.symbol, so_k[-1], so_d[-1])

        # go long if %K line crosses above %D line
        if so_k[-1] >= so_d[-1]:
            if (i not in p) or (i in p and p[i].amount <= 0):
                log.info('long %s (K %s >= D %s)' % v)
                order_percent(i, capital_ppi)

        # go short if %K line crosses below %D line
        else:
            if (i not in p) or (i in p and p[i].amount >= 0):
                log.info('short %s (K %s < D %s)' % v)
                order_percent(i, -capital_ppi)

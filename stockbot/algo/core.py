# -*- coding: utf-8 -*-

'''
algo.core
---------

core functions and objects for stockbot trading algorithms
'''

from __future__ import (
    absolute_import,
    division,
    print_function,
)

from mock import Mock
import numpy as np
from talib import (
    ADX,
    MINUS_DI,
    PLUS_DI,
    SAR,
    STOCH,
)
from zipline.api import (
    order_target_percent,
    symbol,
)
from zipline.errors import SymbolNotFound


def _get_data(data,
              symbol,
              window,
              freq,
              fields,
              fillna,
              fillna_limit):
    '''
    get, validate, fill, and return zipline data

    :param data: zipline data passed to handle_data
    :param symbol: the instrument
    :param window: number of periods in data
    :param freq: e.g. 1d, 1m
    :param fields: e.g. OHLC fields
    :param fillna: fill method (backfill, bfill, pad, ffill, or None)
    :param fillna_limit: max percentage of series that may be filled
    :type data: `zipline.protocol.BarData`
    :type symbol: `zipline.assets.Equity`
    :type window: `int`
    :type freq: `str`
    :type fields: `list` of `str`
    :type fillna: `str`
    :type fillna_limit: `float`
    '''

    input = {f: data.history(symbol, f, window, freq) for f in fields}
    na_pct = [v.isnull().sum()/len(v) for (k, v) in input.items()]

    if any([na > fillna_limit for na in na_pct]):
        return None

    for k in input.keys():
        input[k].fillna(method=fillna, inplace=True)

    return input


def _get_order_target(symbol,
                      order_type,
                      symbols,
                      positions,
                      capital_ppt):
    '''
    determine the proper order target percent

    :param symbol: the instrument
    :param order_type: the direction of the order target, e.g. 'long'
    :param symbols: the universe of instruments
    :param positions: the current portfolio
    :param capital_ppt: the capital % target per instrument
    :type symbol: `zipline.assets.Equity`
    :type order_type: `str`
    :type symbols: `list` of `zipline.assets.Equity`
    :type positions: `list` of positions
    :type capital_ppt: `float`
    '''

    # if symbol is in current positions, get amount, else 0
    position = getattr(positions.get(symbol, object()), 'amount', 0)

    # criteria for closing out an existing position that is no longer traded
    short_cover = [order_type is 'long', symbol not in symbols, position < 0]
    long_sell = [order_type is 'short', symbol not in symbols, position > 0]

    # positions to close
    if all(short_cover) or all(long_sell) or order_type is 'close':
        return 0.0

    # long orders go long
    elif order_type is 'long':
        return capital_ppt

    # otherwise go short
    return -capital_ppt


def init(context,
         name,
         symbols,
         capital_ppt=None,
         fillna=None,
         fillna_limit=0.34,
         log=None,
         **kwargs):
    '''
    zipline trading algorithm generic initialization
    injects parameters into context dict `sbot`

    :param context: context object passed by zipline
    :param name: the name of the trading system for log entries
    :param symbols: the universe of symbols to trade
    :param capital_ppt: capital % per trade
    :param fillna: fill method (backfill, bfill, pad, ffill, or None)
    :param fillna_limit: max percentage of series that may be filled
    :param log: stockbot log
    :type context: `zipline.algorithm.TradingAlgorithm`
    :type name: `str`
    :type symbols: `list` of `str`
    :type capital_ppt: `Decimal`
    :type fillna: `str`
    :type fillna_limit: `float`
    :type log: `logbook.Logger`
    '''

    # create iteration cursor
    context.i = 0

    # initialize log
    log = Mock() if log is None else log

    # validate symbols
    v_symbols = list()

    for s in symbols:
        try:
            v_symbols.append(symbol(s))

        except SymbolNotFound as e:
            log.warning('%s not found, removed' % s)

    # initialize capital_ppt
    capital_ppt = 1.0 / len(v_symbols) if not capital_ppt else capital_ppt

    # store config
    context.sbot = {
        'name': name,
        'symbols': v_symbols,
        'capital_ppt': capital_ppt,
        'fillna': fillna,
        'fillna_limit': fillna_limit,
        'log': log,
        '_order_meta': dict(),
    }
    context.sbot.update(kwargs)

    # log start
    v = (
        context.sbot,
        context.sim_params.start_session,
        context.sim_params.end_session
    )
    context.sbot['log'].info('trading %s from %s to %s' % v)


def adx_rank(context,
             data,
             symbols,
             top_rank=5,
             bot_rank=5,
             di_window=14):
    '''
    rank symbols using ADX and store top_rank, bot_rank

    :param context: the context for the trading system
    :param data: data for the trading system
    :param symbols: the universe of symbols to trade
    :param top_rank: the number of trending instruments to store
    :param bot_rank: the number of oscillating instruments to store
    :param di_window: the base DI window period (ADX window is * 2)
    :type context: `zipline.algorithm.TradingAlgorithm`
    :type data: `zipline.data.data_portal.DataPortal`
    :type symbols: `list` of ...
    :type top_rank: `int`
    :type bot_rank: `int`
    :type di_window: `int`

    expects the following in `context`:

    i
    fillna
    log
    '''

    rank = dict()
    c = context.sbot

    # ensure we have enough history
    if context.i < di_window * 2:
        return

    for s in symbols:

        input = _get_data(
            data,
            symbol=s,
            window=di_window * 2,
            freq='1d',
            fields=['high', 'low', 'close'],
            fillna=c['fillna'],
            fillna_limit=c['fillna_limit'],
        )

        if input is None:
            continue

        try:

            adx = ADX(
                np.array(input['high']),
                np.array(input['low']),
                np.array(input['close']),
            )

            if np.isnan(adx[-1]):
                c['log'].warn('adx for %s is NaN' % s)

            else:
                rank[s] = adx[-1]

        except Exception as e:

            if 'inputs are all NaN' in str(e):
                c['log'].warn('NaN inputs for %s' % s)

            else:  # pragma: no cover
                raise

    c['rank'] = sorted(rank.items(), key=lambda t: t[1], reverse=True)
    c['top'] = c['rank'][:c['top_rank']]
    c['bot'] = c['rank'][-c['bot_rank']:]

    v = (c['top_rank'], c['top'], c['bot_rank'], c['bot'])
    c['log'].info('ranked top %s %s and bot %s %s' % v)


def trade_di(context,
             data,
             t_symbols,
             max_pos,
             di_window=14):
    '''
    zipline trading algorithm that uses the Directional Indicator system
    for trending instruments

    :param context: the context for the trading system
    :param data: data for the trading system
    :param t_symbols: trending instrument symbols
    :param max_pos: maximum number of positions to hold
    :param di_window: the base DI window period (ADX window is * 2)
    :type context: `zipline.algorithm.TradingAlgorithm`
    :type data: `zipline.data.data_portal.DataPortal`
    :type t_symbols: `list` of ...
    :type max_pos: `int`
    :type di_window: `int`

    expects the following in `context`:

    i
    portfolio.positions
    fillna
    log
    capital_ppt
    '''

    c = context.sbot
    p = context.portfolio.positions

    # ensure we have enough history
    if context.i < di_window + 1:
        return

    for s in (list(p) + t_symbols)[:max_pos]:

        input = _get_data(
            data,
            symbol=s,
            window=di_window + 1,
            freq='1d',
            fields=['high', 'low', 'close'],
            fillna=c['fillna'],
            fillna_limit=c['fillna_limit'],
        )

        if input is None:
            continue

        # calculate plus and minus directional movement indicators
        plus_di = PLUS_DI(
            np.array(input['high']),
            np.array(input['low']),
            np.array(input['close']),
            timeperiod=di_window,
        )
        minus_di = MINUS_DI(
            np.array(input['high']),
            np.array(input['low']),
            np.array(input['close']),
            timeperiod=di_window,
        )

        # set order type
        if plus_di[-1] > minus_di[-1]:
            order_type = 'long'
        elif plus_di[-1] < minus_di[-1]:
            order_type = 'short'
        else:
            order_type = 'close'

        # place order
        target = _get_order_target(
            symbol=s,
            order_type=order_type,
            symbols=t_symbols,
            positions=p,
            capital_ppt=c['capital_ppt'],
        )
        order_id = order_target_percent(s, target)

        # store analytic information for order_id
        _meta = {
            'system': 'di',
            'plus_di': PLUS_DI,
            'minus_di': MINUS_DI,
            'order_type': order_type,
            'symbols': t_symbols,
            'positions': p,
        }
        c['_order_meta'][order_id] = _meta


def trade_sar(context,
              data,
              t_symbols,
              max_pos,
              accel=0.02,
              accel_max=0.2):
    '''
    zipline trading algorithm that uses parabolic Stop-And-Reverse points
    for trending instruments

    :param context: the context for the trading system
    :param data: data for the trading system
    :param t_symbols: trending instrument symbols
    :param max_pos: maximum number of positions to hold
    :param accel: the acceleration factor
    :param accel_max: the max acceleration factor
    :type context: `zipline.algorithm.TradingAlgorithm`
    :type data: `zipline.data.data_portal.DataPortal`
    :type t_symbols: `list` of ...
    :type max_pos: `int`
    :type accel: `float`
    :type accel_max: `float`

    expects the following in `context`:

    i
    portfolio.positions
    fillna
    log
    capital_ppt
    '''

    c = context.sbot
    p = context.portfolio.positions

    # ensure we have enough history
    if context.i < 2:
        return

    for s in (list(p) + t_symbols)[:max_pos]:

        input = _get_data(
            data,
            symbol=s,
            window=context.i,
            freq='1d',
            fields=['high', 'low', 'close'],
            fillna=c['fillna'],
            fillna_limit=c['fillna_limit'],
        )

        if input is None:
            continue

        # calculate SARs
        sars = SAR(
            np.array(input['high']),
            np.array(input['low']),
            accel,
            accel_max,
        )

        # set order type
        if input['close'][-1] > sars[-1]:
            order_type = 'long'
        elif input['close'][-1] < sars[-1]:
            order_type = 'short'
        else:
            order_type = 'close'

        # place order
        target = _get_order_target(
            symbol=s,
            order_type=order_type,
            symbols=t_symbols,
            positions=p,
            capital_ppt=c['capital_ppt'],
        )
        order_id = order_target_percent(s, target)

        # store analytic information for order_id
        _meta = {
            'system': 'psar',
            'sars': sars,
            'order_type': order_type,
            'symbols': t_symbols,
            'positions': p,
        }
        c['_order_meta'][order_id] = _meta


def trade_so(context,
             data,
             o_symbols,
             max_pos,
             so_window=14):
    '''
    zipline trading algorithm that uses the Stochastic Oscillator system
    for oscillating instruments

    :param context: the context for the trading system
    :param data: data for the trading system
    :param o_symbols: oscillating instrument symbols
    :param max_pos: maximum number of positions to hold
    :param so_window: the SO window period
    :type context: `zipline.algorithm.TradingAlgorithm`
    :type data: `zipline.data.data_portal.DataPortal`
    :type o_symbols: `list` of ...
    :type max_pos: `int`
    :type so_window: `int`

    expects the following in `context`:

    i
    portfolio.positions
    fillna
    log
    capital_ppt
    '''

    c = context.sbot
    p = context.portfolio.positions

    # ensure we have enough history
    if context.i < so_window + 4:
        return

    for s in (list(p) + o_symbols)[:max_pos]:

        input = _get_data(
            data,
            symbol=s,
            window=so_window + 4,
            freq='1d',
            fields=['high', 'low', 'close'],
            fillna=c['fillna'],
            fillna_limit=c['fillna_limit'],
        )

        if input is None:
            continue

        # calculate stochastic oscillator
        (so_k, so_d) = STOCH(
            np.array(input['high']),
            np.array(input['low']),
            np.array(input['close']),
            fastk_period=so_window,
        )

        # set order type
        if so_k[-1] > so_d[-1]:
            order_type = 'long'
        elif so_k[-1] < so_d[-1]:
            order_type = 'short'
        else:
            order_type = 'close'

        # place order
        target = _get_order_target(
            symbol=s,
            order_type=order_type,
            symbols=o_symbols,
            positions=p,
            capital_ppt=c['capital_ppt'],
        )
        order_id = order_target_percent(s, target)

        # store analytic information for order_id
        _meta = {
            'system': 'so',
            'so_k': so_k,
            'so_d': so_d,
            'order_type': order_type,
            'symbols': o_symbols,
            'positions': p,
        }
        c['_order_meta'][order_id] = _meta

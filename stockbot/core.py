# -*- coding: utf-8 -*-

'''
core
----

core `stockbot` objects and functions
'''

################################################################################


from requests import get
from bs4 import BeautifulSoup


def get_sp500_list(symbols_only=True):
    '''
    obtains a list of S&P500 stocks from wikipedia
    '''

    result = list()

    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    page = get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    rows = soup.find('table').findAll('tr')
    keys = [k.text for k in rows[0].findAll('th')]

    for r in rows[1:]:
        result.append(dict(zip(keys, [f.text for f in r.findAll('td')])))

    return result if not symbols_only else [r['Ticker symbol'] for r in result]

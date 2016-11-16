# -*- coding: utf-8 -*-

'''
portfolio
---------

`stockbot` portfolio classes and functions
'''

################################################################################


from .sources import get_zipline_dp


class Portfolio(object):
    '''
    Class for storing a collection of market instruments
    '''

    def __init__(self, *args, **kwargs):
        '''
        Looks up ticker symbols and stores `zipline` instrument objects
        '''

        # get config settings
        self.bundle = kwargs.pop('bundle', None)
        self.calendar = kwargs.pop('calendar', None)

        self.dataportal = get_zipline_dp(self.bundle, self.calendar)
        self.portfolio = list()

        # populate instruments
        for s in args:
            i = self.dataportal.asset_finder.lookup_symbol(s, None)
            if i not in self.portfolio:
                self.portfolio.append(i)

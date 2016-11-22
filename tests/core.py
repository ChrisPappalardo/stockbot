# -*- coding: utf-8 -*-

'''
tests.core
----------

shared core for `stockbot` unit tests
'''

###############################################################################


def remap(field_map, var):
    '''
    re-maps dict-like var using field_map (from_key: to_key)
    '''

    return dict(
        zip(
            [field_map.get(k, k) for k in var.keys()],
            [var[k] for k in var.keys()]
        )
    )

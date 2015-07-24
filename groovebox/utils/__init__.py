#!/usr/bin/env python
# -*-coding: utf-8 -*-

"""
    utils
    ~~~~~

    Various utilities (not groovebox specific)

    :copyright: (c) 2015 by Mek
    :license: see LICENSE for more details.
"""


def subdict(d, keys):
    """Create a dictionary containing only `keys`
    move to utils
    """
    return dict([(k, d[k]) for k in keys])


def time2sec(t):
    t = str(t)
    if ":" in t:
        m, s = t.split(":")
        return (60 * int(m)) + int(s)
    if "." in t:
        return t.split(".")[0]
    return t

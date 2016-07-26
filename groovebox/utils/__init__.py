#!/usr/bin/env python
# -*-coding: utf-8 -*-

"""
    utils
    ~~~~~

    Various utilities (not groovebox specific)

    :copyright: (c) 2015 by Mek
    :license: see LICENSE for more details.
"""

from datetime import datetime, date
import json
import string


def subdict(d, keys, required=True):
    """Create a dictionary containing only `keys`
    move to utils
    """
    if required:
        return dict([(k, d[k]) for k in keys])
    return dict([(k, d[k]) for k in keys if k in d])


def time2sec(t):
    t = str(t)
    if ":" in t:
        m, s = t.split(":")
        return (60 * int(m)) + int(s)
    if "." in t:
        return t.split(".")[0]
    return t


class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        return json.JSONEncoder.default(self, obj)


class Numcoder(object):

    ALPHABET = string.ascii_uppercase + string.ascii_lowercase + \
        string.digits
    ALPHABET_REVERSE = dict((c, i) for (i, c) in enumerate(ALPHABET))
    BASE = len(ALPHABET)

    @classmethod
    def encode_many(cls, *ns, delim="$"):
        return delim.join([str(cls.encode(n)) for n in ns])

    @classmethod
    def encode(cls, n):
        s = []
        while True:
            n, r = divmod(n, cls.BASE)
            s.append(cls.ALPHABET[r])
            if n == 0: break
        return ''.join(reversed(s))

    @classmethod
    def decode_many(cls, n, delim='$'):
        ns = n.split(delim)
        return [cls.decode(n) for n in ns]

    @classmethod
    def decode(cls, s):
        n = 0
        for c in s:
            n = n * cls.BASE + cls.ALPHABET_REVERSE[c]
        return n



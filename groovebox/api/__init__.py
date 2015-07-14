#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    api/__init__.py
    ~~~~~~~~~~~~~~~

    Groovebox API

    :copyright: (c) 2015 by mek.
    :license: see LICENSE for more details.
"""

import json
import shelve
from .crawler import Crawler
from whoosh.index import open_dir
from whoosh.fields import Schema
from whoosh.qparser import QueryParser
from configs import approot, SONG_DB

def artists():
    """Retrieves list of artists from groovebox json file"""
    return json.load(open("%s/static/data/artists.json" % approot, 'r'))


def concerts(artist=None, concert=None):
    """Retrieves a list of concerts by artist"""
    shows = json.load(open('static/data/concerts.json', 'r'))
    if artist:
        if concert:
            return Crawler.concert(concert)
        return shows[artist]
    return shows


def songs(s=None, db=SONG_DB):
    """Retrieves list of artists from groovebox json file

    Picking py2 v py3 errors may occur with shelve:
    http://stackoverflow.com/questions/25843698/valueerror-unsupported-pickle-protocol-3-python2-pickle-can-not-load-the-file
    """
    with shelve.open(db) as tracks:
        song_index = json.load(open('static/data/song_index.json', 'r'))
        if s:
            if not isinstance(s, (list, tuple)):
                s = [s]
            return [tracks[song_index[int(sid['index'])-1]] for sid in s]
        return song_index


def song(fileid):
    crawler.metadata(artist, song=song)
    pass

def match(query, db="index"):
    """Perform a search, match query against songs, artists, etc"""
    ix = open_dir("%s/%s" % (approot, db))
    with ix.searcher() as searcher:
        q = QueryParser("song", schema=ix.schema).parse(query)
        matches = searcher.search(q, limit=10)
        return [dict(m) for m in matches]



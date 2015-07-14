#!/usr/bin/env pythonNone
#-*-coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~~~~~
    

    :copyright: (c) 2015 by Anonymous
    :license: BSD, see LICENSE for more details.
"""

from flask import render_template, request
from flask.views import MethodView
from views import rest_api
import api

class Artists(MethodView):
    @rest_api
    def get(self, artist=None):
        artists = api.artists()
        return artists[artist] if artist else artists

class Concerts(MethodView):
    @rest_api
    def get(self, artist=None, concert=None):
        return api.concerts(artist=artist, concert=concert)

class Songs(MethodView):
    @rest_api
    def get(self, song=None):
        if song:
            return api.songs(song)
        return [(i+1, j) for i, j in enumerate(api.songs())]

class Search(MethodView):
    @rest_api
    def get(self):
        q = request.args.get('q')
        if not q:
            return []
        matches = api.match(q)
        return [] if not matches else api.songs(matches)


urls = (
    '/artists', Artists,
    '/artists/<artist>', Artists,
    '/artists/<artist>/concerts', Concerts,
    '/artists/<artist>/concerts/<concert>', Concerts,
    '/songs/<int:song>', Songs,
    '/songs', Songs,
    '/search', Search
    )

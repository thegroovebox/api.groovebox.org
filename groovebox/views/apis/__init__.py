#!/usr/bin/env pythonNone
#-*-coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~~~~~
    

    :copyright: (c) 2015 by Anonymous
    :license: BSD, see LICENSE for more details.
"""

from flask import render_template
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
        pass

urls = (
    '/artists', Artists,
    '/artists/<artist>', Artists,
    '/artists/<artist>/concerts', Concerts,
    '/artists/<artist>/concerts/<concert>', Concerts,
    '/songs/<song>', Songs
    )

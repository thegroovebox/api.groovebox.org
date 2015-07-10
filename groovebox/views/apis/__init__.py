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
from api import artists, concerts

class Artists(MethodView):
    @rest_api
    def get(self, artist=None):
        _artists = artists()
        return _artists[artist] if artist else _artists

class Concerts(MethodView):
    @rest_api
    def get(self, concert=None, track=None):
        pass

class Songs(MethodView):
    @rest_api
    def get(self, song=None):
        pass


urls = (
    '/artists', Artists,
    '/artists/<artist>', Artists,
    '/artists/<artist>/concerts', Concerts,
    '/artists/<artist>/concerts/<concert>', Concerts,
    '/artists/<artist>/concerts/<concert>/<int:track>', Concerts,
    '/songs/<song>', Songs
    )

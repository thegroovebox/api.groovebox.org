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
from api.vendors import Crawler
import api.music as api

class Artists(MethodView):
    @rest_api
    def get(self, artist=None):
        if artist:
            return api.Artist.get(tag=artist).dict(tracks=True)
        q = api.Artist.query.with_entities(api.Artist.tag).all()
        return [a.tag for a in q]


class ArtistConcerts(MethodView):
    @rest_api
    def get(self, artist=None, concert=None):
        if not concert:
            q = api.Artist.get(tag=artist).concerts
            return [c.tag for c in q]

        c = api.Concert.get(tag=concert)
        concert = c.dict()
        concert['metadata'] = Crawler.metadata(artist=c.artist.name)
        return concert


class Concerts(MethodView):
    @rest_api
    def get(self, concert=None):
        if not concert:
            limit = request.args.get("limit", 100)
            offset = request.args.get("offset", 0)
            q = api.Concert.query.limit(limit).offset(offset).all()
            return [c.tag for c in q]

        c = api.Concert.get(tag=concert)
        concert = c.dict()
        concert['metadata'] = Crawler.metadata(artist=c.artist.name)
        return concert

    @rest_api
    def post(self, concert=None):
        concert = request.form.get("url", "").split("/")[-1]
        c = api.Concert(tag=concert)
        c.register_tracks()
        return c.dict()
        

class Songs(MethodView):
    @rest_api
    def get(self, song=None):
        limit = request.args.get('limit', 100) 
        offset = request.args.get('offset', 0) 
        if song:
            track = api.Track.get(song).dict()
            return track
        return [[track.id, track.name] for track in \
                    api.Track.query.limit(limit).offset(offset).all()]


class Search(MethodView):
    @rest_api
    def get(self):
        query = request.args.get('q')
        if not query:
            return []

        matching_artists = api.Artist.search(query, field="name", limit=5)
        matching_tracks = api.Track.search(query, field="name", limit=15)
        return {
            'artists': [a.dict() for a in matching_artists],
            'tracks': [t.dict() for t in matching_tracks]
        }


urls = (
    '/artists/<artist>/concerts/<concert>', ArtistConcerts,
    '/artists/<artist>/concerts', ArtistConcerts,
    '/artists/<artist>', Artists,
    '/artists', Artists,
    '/concerts/<concert>', Concerts,
    '/concerts', Concerts,
    '/songs/<int:song>', Songs,
    '/songs', Songs,
    '/search', Search
    )

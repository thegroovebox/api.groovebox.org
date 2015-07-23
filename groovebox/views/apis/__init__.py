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
from views import rest_api, paginate
import api.music as api


class Artists(MethodView):

    @rest_api
    @paginate(limit=100, dump=lambda a: a.tag)
    def get(self):
        return api.db.query(api.Artist.tag)

    @rest_api
    def post(self):
        raise NotImplementedError


class Artist(MethodView):

    @rest_api
    def get(self, artist):
        return api.Artist.get(tag=artist).dict()


class ArtistsConcerts(MethodView):

    @rest_api
    @paginate(limit=100, dump=lambda c: c.tag)
    def get(self, artist):
        return api.Artist.get(tag=artist).concerts_query


class ArtistsConcert(MethodView):

    @rest_api
    def get(self, artist, concert):
        a = api.Artist.get(tag=artist)
        c = api.Concert.get(tag=concert, artist_id=a.id)
        return c.dict(metadata=True)


class ArtistsAlbums(MethodView):

    @rest_api
    @paginate(limit=100)
    def get(self, artist):
        return api.Artist.get(tag=artist).album_query


class ArtistsAlbum(MethodView):

    @rest_api
    def get(self, artist=None, album=None):
        a = api.Artist.get(tag=artist)
        return api.Album.get(id=album, artist_id=a.id).dict(songs=True)


class Albums(MethodView):

    @rest_api
    @paginate(limit=100)
    def get(self):
        return api.Album.query


class Album(MethodView):

    @rest_api
    def get(self, album):
        return api.Album.get(album).dict(songs=True)


class Concerts(MethodView):

    @rest_api
    @paginate(limit=100, dump=lambda c: c.tag)
    def get(self):
        return api.Concert.query

    @rest_api
    def post(self):
        concert = request.form.get("url", "").split("/")[-1]
        try:
            c = api.Concert(tag=concert)
        except:
            pass
        c.register_tracks()
        return c.dict(metadata=True)


class Concert(MethodView):

    @rest_api
    def get(self, concert):
        c = api.Concert.get(tag=concert)
        return c.dict(metadata=True)
        

class Genres(MethodView):

    @rest_api
    @paginate(limit=100)
    def get(self):
        return api.Genre.query

    @rest_api
    def post(self):
        raise NotImplementedError


class Genre(MethodView):

    @rest_api
    def get(self, genre):
        artists = bool(int(request.args.get('artists', 0)))
        return api.Genre.get(genre).dict(artists=artists)


class Tracks(MethodView):

    @rest_api
    @paginate(limit=100, dumps=lambda t: [t.id, t.name])
    def get(self):
        return api.Track.query


class Track(MethodView):

    @rest_api
    def get(self, track):
        return api.Track.get(track).dict()


class Songs(MethodView):

    @rest_api
    @paginate(limit=100, dumps=lambda s: [s.id, s.name])
    def get(self):
        return api.Song.query


class Song(MethodView):

    @rest_api
    def get(self, song):
        return api.Song.get(song)


class Search(MethodView):

    @rest_api
    def get(self):
        query = request.args.get('q')
        page = request.args.get('page', 0)
        if not query:
            return []

        artists = api.Artist.search(query, field="name", limit=5, page=page)
        tracks = api.Track.search(query, field="name", limit=15, page=page)
        return {
            'artists': [a.dict() for a in artists],
            'tracks': [t.dict() for t in tracks]
        }

urls = (
    '/artists/<artist>/albums/<int:album>', ArtistsAlbum, #songs
    '/artists/<artist>/albums', ArtistsAlbums,
    '/artists/<artist>/concerts/<concert>', ArtistsConcert,
    '/artists/<artist>/concerts', ArtistsConcerts,
    '/artists/<artist>', Artist,
    '/artists', Artists,
    '/albums/<album>', Album,
    '/albums', Albums,
    '/genres/<int:genre>', Genre,
    '/genres', Genres,
    '/concerts/<concert>', Concerts,
    '/concerts', Concerts,
    '/tracks/<int:track>', Track,
    '/tracks', Tracks,
    '/songs/<int:song>', Song,
    '/songs', Songs,
    '/search', Search
    )

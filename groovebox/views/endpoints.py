#!/usr/bin/env python
# -*-coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~~~~~
    Groovebox API Endpoints

    :copyright: (c) 2015 by Mek Karpeles
    :license: see LICENSE for more details.
"""

from flask import request
from flask.views import MethodView
from views import rest_api, paginate
from api import music as api
from api.vendors import Archive

class Artists(MethodView):

    @rest_api
    @paginate(limit=100)
    def get(self):
        return api.Artist.query.order_by(api.Artist.name)

    @rest_api
    def post(self):
        artist_id = request.form.get('artist', None)

        try:
            a = api.Artist.get(tag=artist_id)
        except:
            meta = Archive.item_metadata(artist_id)
            name = meta['metadata']['title']
            a = api.Artist(name=name, tag=artist_id)
            a.create()

        results = []
        cids = [c['identifier'] for c in a.get_concerts()]

        for cid in cids:
            try:
                c = api.Concert.get(tag=cid)
            except:
                c = api.Concert(tag=cid, artist_id=a.id)            
                c.create()
            c.register_tracks()

        return a.dict()


class Artist(MethodView):

    @rest_api
    def get(self, artist):
        return api.Artist.get(tag=artist).dict(art=True)


class ArtistsConcerts(MethodView):

    @rest_api
    @paginate(limit=100, dump=lambda c: c.dict(metadata=True, short=True))
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


class ArtistsSongs(MethodView):

    @rest_api
    @paginate(limit=100)
    def get(self, artist):
        return api.Artist.get(tag=artist).songs_query


class ArtistsTracks(MethodView):

    @rest_api
    @paginate(limit=100)
    def get(self, artist):
        return api.Artist.get(tag=artist).tracks_query


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
        artist = request.form.get('artist', '')
        atag = artist.replace(' ', '')
        concert = request.form.get("url", "").split("/")[-1]
        try:
            a = api.Artist.get(tag=atag)
        except:
            a = api.Artist(name=artist, tag=atag)
            a.create()
        try:
            c = api.Concert.get(tag=concert)
        except:
            try:
                c = api.Concert(tag=concert, artist_id=a.id)            
                c.create()
            except:
                return {'error': 'Concert already registered'}
        if c.tracks:
            return {'error': 'Concert already has tracks'}
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
    @paginate(limit=100, dump=lambda t: [t.id, t.name])
    def get(self):
        return api.Track.query


class Track(MethodView):

    @rest_api
    def get(self, track):
        return api.Track.get(track).dict()


class Songs(MethodView):

    @rest_api
    @paginate(limit=25)
    def get(self):
        return api.Song.query


class Song(MethodView):

    @rest_api
    def get(self, song):
        return api.Song.get(song).dict()


class SongTracks(MethodView):

    @rest_api
    def get(self, song):
        return [t.dict() for t in api.Song.get(song).tracks]


class Search(MethodView):

    @rest_api
    def get(self):
        query = request.args.get('q')
        page = request.args.get('page', 0)

        if not query:
            return []

        artists = api.Artist.search(query, field="name", limit=5, page=page)
        tracks = api.Track.search(query, field="name", limit=10, page=page)
        #  albums = api.Album.search(query, field="name", limit=3, page=page)
        #  songs = api.Song.search(query, field="name", limit=5, page=page)
        return {
            #'songs': [s.dict() for s in songs],
            #'albums': [a.dict() for a in albums],
            'artists': [a.dict() for a in artists],
            'tracks': [t.dict() for t in tracks]
        }


class ZeroClick(MethodView):

    @rest_api
    def get(self):
        artist = request.args.get('artist', None)
        title = request.args.get('title', None)
        try:
            track = api.Track.search(title, field="name", limit=1)[0]
            return {'url': request.url_root.replace('//api.', '//') \
                        + "?queue=%s" % track.id,
                    'artist': track.artist.name,
                    'title': track.name
                    }
        except:
            return None


class Index(MethodView):

    @rest_api
    def get(self):
        urlbase = request.url_root[:-1]
        return dict([(urls[i+1].__name__.split(".")[-1].lower(),
                      urlbase + urls[i])
                     for i in range(len(urls))[::2]])


urls = (
    '/artists/<artist>/albums/<int:album>', ArtistsAlbum,  # songs
    '/artists/<artist>/albums', ArtistsAlbums,
    '/artists/<artist>/concerts/<concert>', ArtistsConcert,
    '/artists/<artist>/concerts', ArtistsConcerts,
    '/artists/<artist>/songs', ArtistsSongs,
    '/artists/<artist>/tracks', ArtistsTracks,
    '/artists/<artist>', Artist,
    '/artists', Artists,
    '/albums/<album>', Album,
    '/albums', Albums,
    '/genres/<int:genre>', Genre,
    '/genres', Genres,
    '/concerts/<concert>', Concert,
    '/concerts', Concerts,
    '/tracks/<int:track>', Track,
    '/tracks', Tracks,
    '/songs/<int:song>/tracks', SongTracks,
    '/songs/<int:song>', Song,
    '/songs', Songs,
    '/instasearch', ZeroClick,
    '/search', Search,
    '/', Index
    )

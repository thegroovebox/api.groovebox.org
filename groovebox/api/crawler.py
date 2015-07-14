#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    api.crawler.py
    ~~~~~~~~~~~~~~

    Provides utilities for crawling songs, retrieving song metadata,
    and building search indices.

    :copyright: (c) 2015 by mek.
    :license: see LICENSE for more details.
"""

import json
import requests
import shelve
from whoosh.index import create_in
from whoosh.fields import Schema, ID, TEXT
from utils import subdict
from configs import approot, SONG_DB

BASE_URL = "https://archive.org"
API_URL = "%s/advancedsearch.php" % BASE_URL
METADATA_URL = "%s/metadata" % BASE_URL
COVERART_API_URL = "https://itunes.apple.com/search"
REQUIRED_KEYS = ['track', 'title', 'album', 'length', 'name', 'creator']
FILETYPE_PRIORITY = ['mp3', 'shn', 'flac', 'ogg']

class Worker(object):
        
    @staticmethod
    def register_songs(db, artist, concert):
        """Registers the songs from a concert. Constructs a dictionary
        of track names within this concert mapped to metadata.
        
        params:
            db - a `shelve` instance
            artist - the collection / Archive.org id of artist 
        """
        for track in Crawler.tracks(concert):
            title = track.get('title')
            track['concert'] = concert
            if title in db:
                if artist in db[title]:
                    db[title][artist].append(track)
                else:
                    db[title][artist] = [track]
            else:
                db[title] = {artist: [track]}

    @classmethod
    def crawl_artist(cls, artist, artists=None, db=SONG_DB):
        """
        Crawls a single artists concerts and adds their songs/tracks
        to the shelve database (whose name is specified by `db`).

        If no 'artists' dict is provided, assume this is a one off
        crawl of a single artist and then rebuild the song_index.json

        params:
            artist - the archive.org ID of the artist (e.g. "GratefulDead")
            artists - (optional) a dict of artists (passed from def
                      `crawl`) or None if crawl_artist should lookup
                      the artist itself in concerts.json
            db - the shelve db where data is read/written from
        """        
        concerts = artists[artist]['concerts'] if artists else \
            json.load(open('static/data/concerts.json', 'r'))[artist]['concerts']
        for concert in concerts:
            print(concert)
            with shelve.open(db) as index:
                cls.register_songs(index, artist, concert)
        if not artists:
            cls.build_song_list(db=db)


    @classmethod
    def crawl(cls, db=SONG_DB, start=0, end=None, artist=None):
        """Crawls all artist's concerts and build an index of their
        songs, keyed by song name. Results are stored in a shelve db.

        example:
          {
            "Song Name 1": {"Artist 1": [{track rendition 1}, {track rendition 2}],
                            "Artist 2": [{track rendition 1}],
                           },
            "Song Name 2": {...}
          }

        """
        artists = json.load(open('static/data/concerts.json', 'r'))
        for i, artist in enumerate(artists):
            print(artist)
            if i >= start:
                if not end or i < end:
                    cls.crawl_artist(artist, artists=artists, db=db)
        cls.build_song_list(db=db)


    @classmethod
    def build_song_list(cls, db=SONG_DB):
        """Build an index/list of unique song names mapped to int id"""
        with shelve.open(db) as tracks:
            with open('%s/static/data/song_index.json' % approot, 'w') as song_index:
                json.dump(list(tracks.keys()), song_index)


    @staticmethod
    def build_search_index(db=SONG_DB):
        """Rebuild the whoosh search index of songs"""
        song_index = json.load(open('static/data/song_index.json', 'r'))
        schema = Schema(song=TEXT(stored=True), index=ID(stored=True))
        ix = create_in("%s/index" % approot, schema)
        writer = ix.writer()
        
        for i, song in enumerate(song_index):
            writer.add_document(song=song, index=str(i+1))
        writer.commit()


class Crawler(object):

    def __init__(self):
        pass


    @staticmethod
    def concerts(artist, limit=20000):
        """Retrieves all the concerts (items) of a band from Archive.org API
        
        params:
            artist - the collection id for this artist (e.g. GratefulDead)
        """
        params = {
            "q": "collection:(%s)" % artist,
            "fl[]": "identifier",
            "rows": limit,
            "output": "json"
            }
        return requests.get(API_URL, params=params).json()


    @classmethod
    def concert(cls, c):
        """Retrieves a concert's metadata + tracks from Archive.org API"""
        url = "%s/%s" % (METADATA_URL, c)
        r = requests.get(url).json()
        fs = r.pop('files')
        r = r.pop('metadata', {})
        try:
            r['tracks'] = cls._tracks(fs)
        except Exception as e:
            return e
        try:
            r['metadata'] = cls.metadata(r['creator'])
        except Exception as e:
            return e
        return r


    @classmethod
    def tracks(cls, c):
        """Returns ordered list of tracks for this concert"""
        url = "%s/%s" % (METADATA_URL, c)
        r = requests.get(url).json()
        fs = r.pop('files')
        return cls._tracks(fs)


    @staticmethod
    def metadata(artist, song=""):
        """Retrieves coverart + details about song, album, and artist
        from itunes.

        http://www.apple.com/itunes/affiliates/resources/documentation
            /itunes-store-web-service-search-api.html
        """        
        keep_keys = ["primaryGenreName", "coverArt"] + \
            (["collectionName", "trackName", "releaseDate"] if song else [])
        r = requests.get(COVERART_API_URL, params={
                "media": "music",
                "artistName": artist,
                "term": song or artist, #if no song available
                "country": "us",
                "limit": 1
                }).json()['results'][0]
        r["coverArt"] = r["artworkUrl100"].replace('.100x100-75', '')
        return dict([(key, r[key]) for key in keep_keys])


    @staticmethod
    def _tracks(files):
        """Returns a sorted list of tracks given Archive.org item
        (concert) metadata files
        """
        def sort_tracks(tracks):
            return sorted(ts, key=lambda t: int(t['track'].split("/")[0]))

        def get_filetype(files):
            available = set(f.get('name', '').lower().rsplit('.', 1)[-1] for f in files)
            return next(ft if ft in available else False for ft in FILETYPE_PRIORITY)

        ts = []
        filetype = get_filetype(files)

        if not filetype:        
            return {} # better error handling required

        for f in files:
            try:
                track = subdict(f, REQUIRED_KEYS)
            except KeyError as e:            
                continue # Skip if track doesn't have required keys

            title = track.get('title')
            if track['name'].endswith(filetype):
                ts.append(track)

        try:
            return sort_tracks(ts)
        except ValueError as e:
            print(e)
        return ts

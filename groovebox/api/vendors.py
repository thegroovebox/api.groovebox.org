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
from math import ceil
from whoosh.index import create_in
from whoosh.fields import Schema, ID, TEXT
from sqlalchemy.exc import IntegrityError
from utils import subdict


BASE_URL = "https://archive.org"
API_URL = "%s/advancedsearch.php" % BASE_URL
METADATA_URL = "%s/metadata" % BASE_URL
COVERART_API_URL = "https://itunes.apple.com/search"
REQUIRED_KEYS = ['title', 'length', 'name', 'track']
FILETYPE_PRIORITY = ['mp3', 'shn', 'ogg', 'flac']
                                                

class Crawler(object):

    @staticmethod
    def artists(limit=10000):
        """Retrieves a list of artists from the Archive.org Live Music
        collection
        """
        params = {
            "q": "collection(etree) AND mediatype:(collection)",
            "fl[]": "identifier title",
            "rows": limit,
            "output": "json"
            }
        r = requests.get(API_URL, params=params).json()['response']['docs']
        return list(filter(lambda r: r['identifier'] != 'etree', r))


    @staticmethod
    def concerts(artist, limit=15000):
        """Retrieves all the concerts (items) of a band from Archive.org API
        
        params:
            artist - the collection id for this artist (e.g. GratefulDead)
        """
        params = {
            "q": "collection:(%s)" % artist,
            "fl[]": "identifier title",
            "rows": limit,
            "output": "json"
            }
        rs = requests.get(API_URL, params=params).json()['response']['docs']
        return rs


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
    def tracks(cls, concert):
        """Returns ordered list of tracks for this concert"""
        url = "%s/%s" % (METADATA_URL, concert)
        try:
            r = requests.get(url).json()
            fs = r.pop('files')
        except:
            fs = []
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
            for i in range(len(tracks)):
                try:
                    tracks[i]['track'] = int(tracks[i].get('track', "1").split("/")[0])
                except:
                    tracks[i]['track'] = 1

            return sorted(tracks, key=lambda t: t['track'])

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

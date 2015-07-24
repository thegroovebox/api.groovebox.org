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

import requests
from difflib import SequenceMatcher
from utils import subdict

REQUIRED_KEYS = ['title', 'length', 'name', 'track']
FILETYPE_PRIORITY = ['mp3', 'shn', 'ogg', 'flac']


class Vendor(object):
    BASE_URL = ""


class Archive(Vendor):
    BASE_URL = 'https://archive.org'
    METADATA_URL = '%s/metadata' % BASE_URL

    @classmethod
    def filenames(cls, item):
        url = "%s/%s" % (cls.METADATA_URL, item)
        try:
            r = requests.get(url).json()
        except:
            r = {}
        return r.pop('files', [])


class Musix(Vendor):
    BASE_URL = 'https://www.musixmatch.com'
    API_URL = '%s/ws/1.1' % BASE_URL
    API_PARAMS = {
        'app_id': 'community-app-v1.0',
        'format': 'json'
        }

    @classmethod
    def artist(cls, artist, albums=True, tracks=False, image=False, limit=5):
        """Use this to get an artist and their albums"""
        options = {
            "limit": limit
            }
        if image:
            options['artist_image'] = 1

        try:
            artists = cls.search(artist, entity='artist', **options)
            match = max(artists, key=lambda candidate: SequenceMatcher(
                None, artist, candidate['artist']['artist_name']).ratio())
        except:
            return {}

        if albums:
            artist_id = match.get('artist', {}).get('artist_id')
            match['albums'] = [] if not artist_id else \
                cls.albums(artist_id, tracks=tracks)
        return match

    @classmethod
    def albums(cls, artist_id, tracks=False, page=1):
        """artist-id is the Artist's Musix id"""
        url = '%s/artist.albums.get' % cls.API_URL
        params = cls.API_PARAMS
        params.update({
            'page_size': 100,
            'page': page,
            'g_album_name': 1,
            'artist_id': artist_id
            })
        if tracks:
            pass

        return requests.get(url, params=params).json() \
            .get('message', {}).get('body', {}).get('album_list', [])

    @classmethod
    def album_tracks(cls, album_id, page=1):
        """Return tracks of an album by musix album id. This method
        assumes no album will have more than 100 songs, or if it does,
        this is rare enough that it can be manually QA'd
        """
        url = '%s/artist.albums.get' % cls.API_URL
        params = cls.API_PARAMS
        params.update({
            "part": "track_artist",
            "track_fields_set": "community_track_list",
            "artist_fields_set": "community_track_list_artist",
            "page_size": 100,
            "page": page
            })
        return requests.get(url, params=params).json() \
            .get('body', {}).get('track_list', [])

    @classmethod
    def tracks(cls, track, artist=False, limit=100):
        """
        url = "%s/album.tracks.get" % cls.API_URL
        params = cls.API_PARAMS
        params.update({
                "page_size": limit,
                "f_stop_words": 1,
                "g_album_name_type": 1,
                "part": "track_artist",
                "track_fields_set": "community_track_list",
                "artist_fields_set": "community_track_list_artist"
                "album_id": artist
                })
        if artist:
            options['track_artist'] = 1

        # "track_fields_set": "community_track_list",
        # "artist_fields_set": "community_track_list_artist",
        # "q_track_artist": artist,

        results = [] # if multiple pages
        # may have to search multiple pages
        tracks = cls.search(track, **options)
        return tracks
        """
        raise NotImplementedError

    @classmethod
    def search(cls, q, entity='track', limit=71, page=1, **options):
        """Search for an artist or track's metadata via musixmatch API

        params:
            limit - max 71 for tracks and artists (trial and error)
            options - kwargs of params to include with GET request:
                part=["track_artist"|"artist_image"]
                    track_artist - returns artist w/ each track
                    artist_image - includes artist images w/ each artist

        usage:
            >>> artist = Musix.search(entity="artist", part="artist_image")
        """
        url = '%s/%s.search' % (cls.API_URL, entity)
        params = cls.API_PARAMS
        params.update({
            "q": q,
            "page": page,
            "page_size": limit,  # max page size (trial and error)
            "f_stop_words": 1,
            "g_album_name_type": 1,
            })
        params.update(options)
        r = requests.get(url, params=params).json()
        return r.get('message', {}).get('body', {}).get('%s_list' % entity, [])


class Itunes(Vendor):
    BASE_URL = 'https://itunes.apple.com'
    SEARCH_URL = '%s/search' % BASE_URL

    @classmethod
    def artist(cls, artist, limit=1):
        return cls.search(artist=artist, limit=limit)

    @classmethod
    def song(cls, song, artist="", limit=1):
        return cls.search(artist=artist, song=song, limit=limit)

    @classmethod
    def search(cls, artist="", song="", limit=1):
        """Retrieves metadata + coverart about song, album, and artist
        from itunes.

        http://www.apple.com/itunes/affiliates/resources/documentation
            /itunes-store-web-service-search-api.html
        """
        params = {
            "media": "music",
            "artistName": artist,
            "term": song or artist,  # if no song available
            "country": "us",
            "limit": limit
            }
        r = requests.get(cls.SEARCH_URL, params=params).json()
        results = r.get('results', [])
        for i, r in enumerate(results):
            results[i]['coverArt'] = results[i]["artworkUrl100"]\
                .replace('.100x100-75', '')
        return results


class Musicbrainz(Vendor):
    BASE_URL = 'https://musicbrainz.org'


class Crawler(object):

    """XXX Crawler should be refactored and considered as a candidate
    for deprecation (in favor of its useful components being moved to
    Archive Vendor)
    """

    @staticmethod
    def artists(limit=15000):
        """Retrieves a list of artists from the Archive.org Live Music
        collection.

        params:
            limit - default 15,000 as no music collection I know of
                    has more than 15,000 items.
        """
        params = {
            "q": "collection:(etree) AND mediatype:(collection)",
            "fl[]": "identifier title",
            "rows": limit,
            "output": "json"
            }
        r = requests.get(Archive.API_URL, params=params).json()
        rs = r['response']['docs']
        return list(filter(lambda r: r['identifier'] != 'etree', rs))

    @staticmethod
    def concerts(artist, limit=15000):
        """Retrieves all the concerts (items) of a band from
        Archive.org API.

        params:
            artist - the collection id for this artist
                    (e.g. GratefulDead)
        """
        params = {
            "q": "collection:(%s)" % artist,
            "fl[]": "identifier title",
            "rows": limit,
            "output": "json"
            }
        r = requests.get(Archive.API_URL, params=params).json()
        return r['response']['docs']

    @classmethod
    def concert(cls, c):
        """Retrieves concert metadata + tracks from Archive.org"""
        url = "%s/%s" % (Archive.METADATA_URL, c)
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
        return cls._tracks(Archive.filenames(concert))

    @staticmethod
    def metadata(artist):
        data = {
            "primaryGenreName": "",
            "coverArt": ""
            }
        metadata = Itunes.artist(artist)
        if not metadata:
            return data

        song = metadata[0]
        keep_keys = data.keys()
        for key in song:
            if key in keep_keys:
                data[key] = song[key]
        return data

    @staticmethod
    def _tracks(files):
        """Returns a sorted list of tracks given Archive.org item
        (concert) metadata files
        """
        def sort_tracks(tracks):
            for i in range(len(tracks)):
                try:
                    tracks[i]['track'] = int(tracks[i].get('track', "1")
                                             .split("/")[0])
                except:
                    tracks[i]['track'] = 1
            return sorted(tracks, key=lambda t: t['track'])

        def get_filetype(files):
            available = set(f.get('name', '').lower()
                            .rsplit('.', 1)[-1] for f in files)
            return next(ft if ft in available else
                        False for ft in FILETYPE_PRIORITY)

        ts = []
        filetype = get_filetype(files)

        if not filetype:
            return {}  # better error handling required

        for f in files:
            try:
                track = subdict(f, REQUIRED_KEYS)
            except KeyError as e:
                continue  # Skip if track doesn't have required keys

            if track['name'].endswith(filetype):
                ts.append(track)

        try:
            return sort_tracks(ts)
        except ValueError as e:
            print(e)
        return ts

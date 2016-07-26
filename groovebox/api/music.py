#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    api/music.py
    ~~~~~~~~~~~~

    Groovebox Music API

    :copyright: (c) 2015 by mek.
    :license: see LICENSE for more details.
"""

from random import randint
import requests
from datetime import datetime
from sqlalchemy import Column, Unicode, BigInteger, Integer, \
    DateTime, ForeignKey, Table, exists, func
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.orm import relationship
from api import db, engine, core
from api.vendors import Crawler, Musix, Archive, Itunes
from utils import time2sec


def coldstart(concerts=True, tracks=False, crawl=False):
    """Build tables, get artists and their concerts and insert
    into the database. If crawl is specified, retrieve tracks from
    each artist's concerts and then rebuild whoosh search index.

    Warning: Artist.register(concerts=True, tracks=True) has the
    disadvantage of not being very parallelizable. Instead, consider
    registering Artists and Concerts first,
    i.e. Artist.register(concerts=True), and then running
    Track.register() (it is recommended you use multiple threads or
    separate processes) to batch register tracks for any concert not
    having any tracks registered.

    usage:
    >>> from api.crawler import Worker;Worker.coldstart()
    """
    build_tables()
    Artist.register(concerts=concerts, tracks=tracks)  # populate db


def build_tables():
    """Builds database postgres schema"""
    from sqlalchemy import MetaData
    MetaData().create_all(engine)


def report():
    """Generates a statistical report of database coverage compared to
    available data
    """
    tracks_with_songs = Track.query\
        .filter(Track.song_id is not None).count()
    songs_with_tracks = db.query(Track.song_id)\
        .distinct(Track.song_id).filter(Track.song_id is not None).count()
    concerts = Concert.query.count()
    trackless = Concert.trackless_concerts(query=True).count()

    return {
        "artists": Artist.query.count(),
        "concerts": concerts,
        "trackless_concerts": trackless,
        "complete_concerts": concerts - trackless,
        "songs": {
            "total": Song.query.count(),
            "with_tracks": songs_with_tracks
            },
        "tracks": {
            "total": Track.query.count(),
            "with_songs": tracks_with_songs
            }
        }


artist_to_genre = \
    Table('artists_genres', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('artist_id', BigInteger,
                 ForeignKey('artists.id', use_alter=True),
                 nullable=False),
          Column('genre_id', BigInteger,
                 ForeignKey('genres.id', use_alter=True),
                 nullable=False)
          )


song_to_album = \
    Table('song_albums', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('song_id', BigInteger,
                 ForeignKey('songs.id', use_alter=True),
                 nullable=False),
          Column('album_id', BigInteger,
                 ForeignKey('albums.id', use_alter=True),
                 nullable=False)
          )


class Genre(core.Base):
    """Jazz, Classical, Funk, Jam, Reggae, Ambient, Blue"""

    __tablename__ = "genres"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    name = Column(Unicode, unique=True, nullable=False)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

    def dict(self, artists=False):
        genre = super(Genre, self).dict()
        genre.pop("created")
        if artists:
            genre['artists'] = [a.dict() for a in self.artists]
        return genre


class Artist(core.Base):

    __tablename__ = "artists"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    tag = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)
    mbid = Column(Unicode, nullable=True, default=None,
                  unique=True)  # musicbrainz id
    musixmatch = Column(Unicode, unique=True)
    avatar = Column(Unicode, default=u"")
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)
    genres = relationship('Genre', secondary=artist_to_genre,
                          backref="artists")
    album_query = relationship('Album', lazy='dynamic')
    concerts_query = relationship('Concert', lazy='dynamic')

    # XXX If song has tracks
    songs_query = relationship('Song', lazy='dynamic')
    tracks_query = relationship('Track', lazy='dynamic')

    def get_concerts(self):
        try:
            return requests.get("https://api.archivelab.org/search?q=collection:(" + self.tag + ")%20AND%20mediatype:(audio)&limit=1000").json()['response']['docs']
        except KeyError:
            return []

    def get_metadata(self):
        return Archive.get_metadata(self.tag)

    @classmethod
    def register(cls, artist=None, concerts=False, tracks=False, start=0):
        """Retrieves a json list of all artists from the Live Music
        collection from Internet Archive (archive.org) and then
        creates an Artist entry within the databse for each artist. If
        specified within params, additionally registers their concerts
        (items) and the concert's tracks (files).

        params:
        artist - register a single artist (by [collection] name)
        concerts - register artists' concerts?
        tracks - register concerts tracks? Requires concerts=True

        usage:
        >>> from api.music import Artist
        >>> Artist.register()
        """
        artists = [artist] if artist else Crawler.artists()
        for a in artists[start:]:
            tag = a['identifier']
            name = a['title']
            try:
                cls(tag=tag, name=name).create()
            except:
                pass
            if concerts:
                cls.register_concerts(artist=a, tracks=tracks)

    def register_concerts(self, tracks=False):
        """Retrieves a json list of concerts from archive.org for a
        given Artist (one which is already registered with our
        database) and registers the artist's concerts with our
        db. Additionally registers the tracks of each of these
        concerts if tracks=True.

        usage:
        >>> from api.music import Artist
        >>> a = Artist.get(tag="ExplosionsintheSky")
        >>> a.register_concerts()
        """
        concerts = Crawler.concerts(self.tag)
        for concert in concerts:
            name = concert['title']
            tag = concert['identifier']
            print(concert)
            try:
                c = Concert(tag=tag, name=name, artist_id=self.id)
                c.create()
                self.concerts.append(c)
                self.save()
            except:
                pass

            if tracks:
                c.register_tracks()

    def register_tracks(self, concert=None):
        """Assumes Artist and Artist's Concerts already exist in
        database. Retrieve data for all tracks within this Artist's
        Concerts (or a single concert, if specified)
        """
        concerts = [concert] if concert else self.concerts
        [c.register_tracks() for c in concerts]

    def registeralbums(self, artist_id=None):
        if artist_id and not self.musixmatch:
            self.musixmatch = artist_id
        if self.musixmatch:
            return Musix.albums(self.musixmatch)

    def register_songs(self, recrawl=False):
        for album in self.albums:
            if recrawl or not album.songs:
                album.register_songs()

    def resolve_songs(self):
        """In some cases, metadata results in an artist which has
        several songs which are semantically the same but have
        different names:

        e.g. "Touch of Grey", "Touch of Grey (Live)"

        These should be considered the same songs. This function
        naively entity resovles multiple songs of an Artist into 1
        song (programmer is shown a list of songs and is promoted to
        select which songs are merged into which master song) and then
        updates the Artist's albums to point to correct master song.
        """
        def merge_songs(s1, s2):
            """Merges song s2 into s1. s2 gives its tracks to s1. s2's
            albums switch pointer to s1 in song_to_album
            """
            print("merging %s into %s" % (s1.name, s2.name))

            # s1.tracks.extends(set(s1.tracks) - set(s2.tracks))
            "update table song_albums set song_id = s1.id"
            "where song_id = s2.id"
            # in song_to_album
            # change s.id to master_track.id
            # raw sql, change s.id to master_track.id

        offset = 0
        while True:
            # get first song by this artist
            song = Song.query.filter(Song.artist_id == self.id)\
                .offset(offset).first()

            # If we've reached the end
            if not song:
                break

            # get all songs by this artist whose names are like `song`
            songs = Song.query.filter(Song.artist_id == self.id)\
                .filter(Song.name.ilike("%" + song.name + "%")).all()

            # get id of master and songs to merge from user
            for i, s in enumerate(songs):
                print(i, s.name)
            merge = list(map(int, input("Merge (e.g. 1,2,3): ").split(",")))
            master = int(input("Into (e.g. 4): "))

            master_track = songs[master]
            for i, s in enumerate(songs):
                if i in merge:
                    merge_songs(master_track, s)
                    pass
            break

    def discography(self, songs=False):
        """Creates a discography for this artist by:"

        1. Updating the Artist with metadata + genres
        2. Creating a db entry for each of the Artist's `Albums`
        3. For each album, create (if !exists) or fetch Song and map
        to Album
        4. For each Song, map Tracks whose titles match with >80%
        confidence
        """
        def fillin_artist(m):
            self.musixmatch = m['artist']['artist_id']
            self.mbid = m['artist']['artist_mbid'] or None
            genres = [x['music_genre']['music_genre_name'] for x in
                      m['artist']['primary_genres']['music_genre_list']]
            for genre in genres:
                try:
                    g = Genre.get(name=genre)
                    if g not in self.genres:
                        self.genres.append(g)
                except:
                    self.genres.append(Genre(name=genre))

        def create_albums(albums, songs=False):
            albums = m['albums']
            for data in albums:
                album = data['album']
                try:
                    a = Album.get(musixmatch=album['album_id'])
                except:
                    a = Album(name=album['album_name'],
                              mbid=album['album_mbid'] or None,
                              musixmatch=album['album_id'],
                              coverart=album['album_coverart_800x800'])
                    self.albums.append(a)
                if songs:
                    a.register_songs()

        m = Musix.artist(self.name, albums=True)
        fillin_artist(m)
        create_albums(m['albums'])
        self.save()

    def get_deduped_tracks(self):
        """Placeholder for resolving Tracks against Songs"""
        # tracks = {}
        tracknames = db.query(func.lower(Track.name)) \
            .filter(self.id == Track.artist_id).all()
        for trackname in tracknames:
            pass

    def dict(self, tracks=False, albums=False, art=False):
        if not self.avatar and art:
            try:
                metadata = Itunes.search(artist=self.name)[0]
                self.avatar = metadata.get('coverArt')
                self.save()
            except:
                pass
        
        artist = super(Artist, self).dict()
        artist['genres'] = [g.dict() for g in self.genres]
        if tracks:
            artist['tracks'] = [t.dict() for t in self.tracks]
        if albums:
            artist['albums'] = [a.dict() for a in self.albums]
        return artist


class Album(core.Base):

    __tablename__ = "albums"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    artist_id = Column(BigInteger, ForeignKey('artists.id'), nullable=False)
    name = Column(Unicode, nullable=False)
    mbid = Column(Unicode, unique=True)
    musixmatch = Column(Unicode, unique=True)
    coverart = Column(Unicode, default=None)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

    artist = relationship('Artist', backref='albums')
    songs = relationship('Song', secondary=song_to_album,
                         backref="albums")


    @classmethod
    def resolve_songs(cls):
        """Resolve tracks to their songs.
        TODO make work like Track.register; multi-threadable

        for each tracks, find all songs by artist_id
        """
        for album in Album.query.all():
            for song in album.songs:
                if not song.tracks:
                    #  select tracks with artist_id
                    tracks = Track.query.filter(Track.artist_id == album.artist_id)\
                        .filter(Track.name.ilike("%" + song.name + "%")).all()
                    for track in tracks:
                        print("%s -is- %s" % (track.name, song.name))
                        if not track.song_id:
                            track.song_id = song.id
                            track.save()

    def register_songs(self):
        """Discovers and creates db entries for the Songs of this
        Album through the musixmatch api.

        usage:
        >>> from api.music import Artist
        >>> a = Artist.get(tag="ExplosionsintheSky")
        >>> a.albums[0].register_songs()
        """
        songs = Musix.album_songs(self.musixmatch)
        for song in songs:
            print(song)
            try:
                s = Song.get(musixmatch=str(song['track_id']))
            except core.GrooveboxException:
                s = Song(musixmatch=str(song['track_id']),
                         name=song['track_name'],
                         artist_id=self.artist_id)
                s.create()
            s.albums.append(self)

            try:
                s.save()
            except Exception:
                db.remove()

    def dict(self, songs=False):
        album = super(Album, self).dict()
        album.pop('artist_id')
        album['artist'] = self.artist.dict()
        if songs:
            album['songs'] = [s.dict() for s in self.songs]
        return album


class Song(core.Base):

    """A song is an entity-resolved composition which is unique per
    Artist. A song, while unique, may belong to several (but not none)
    of an Artist's albums. This is enforced necessarily by the
    Album.songs relationship w/ a secondary to a `song_to_album`
    mapping.
    """

    __tablename__ = "songs"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    artist_id = Column(BigInteger, ForeignKey('artists.id'), nullable=False)
    musixmatch = Column(Unicode, unique=True)
    name = Column(Unicode, nullable=False)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

    artist = relationship('Artist', backref='songs')
    tracks = relationship('Track', backref='song')

    def dict(self):
        song = super(Song, self).dict()
        song['artist'] = self.artist.dict()
        song['albums'] = [a.dict() for a in self.albums]
        return song


class Concert(core.Base):

    __tablename__ = "concerts"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    artist_id = Column(BigInteger, ForeignKey('artists.id'), nullable=False)
    tag = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

    artist = relationship('Artist', backref='concerts')

    @classmethod
    def trackless_concerts(cls, limit=None, offset=None, query=False):
        q = Concert.query\
            .filter(~exists().where(Track.concert_id == Concert.id))\
            .limit(limit).offset(offset)
        return q if query else q.all()

    @classmethod
    def crawl(cls, limit=1000, offset=0, end=None):
        """Crawls every registered concert to register_tracks"""
        concerts = Concert.query.limit(limit).offset(offset).all()
        for concert in concerts:
            try:
                cls.register_tracks(concert.tag)
            except Exception as e:
                print(e)

    def register_tracks(self):
        """Retrieves json metadata, including filenames, from
        archive.org for a concert (one which is already registered
        with our database) and inserts the concert's tracks (files)
        with our db.

        >>> from api.music import Concert
        >>> a = Artist.get(tag="ExplosionsintheSky")
        >>> [c.register_tracks() for c in a.concerts]
        """
        for track in Crawler.tracks(self.tag):
            print(track['name'])
            try:
                t = Track(
                    artist_id=self.artist_id,
                    concert_id=self.id,
                    item_id=self.tag,
                    file_id=track['name'],
                    number=track['track'],
                    name=track['title'],
                    length=time2sec(track['length'])
                    )
                t.create()
                self.tracks.append(t)
                self.save()
            except (IntegrityError, InvalidRequestError) as e:
                print(e)

    def dict(self, metadata=False, short=False):
        concert = super(Concert, self).dict()
        if not short:
            concert['artist'] = self.artist.name
            concert['tracks'] = sorted([track.dict() for track in self.tracks],
                                       key=lambda x: x['number'])
        if metadata:
            try:
                concert['metadata'] = Crawler.metadata(artist=self.artist.name)
            except Exception as e:
                concert['metadata'] = {"error": str(e)}
        return concert


class Track(core.Base):

    __tablename__ = "tracks"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    artist_id = Column(BigInteger, ForeignKey('artists.id'), nullable=False)
    concert_id = Column(BigInteger, ForeignKey('concerts.id'), nullable=False)
    item_id = Column(Unicode, nullable=False)
    file_id = Column(Unicode, nullable=False)
    song_id = Column(BigInteger, ForeignKey('songs.id'), nullable=True)
    number = Column(Integer, nullable=False)

    name = Column(Unicode)
    length = Column(Integer)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

    concert = relationship('Concert', backref='tracks')
    artist = relationship('Artist', backref='tracks')

    @classmethod
    def register(cls, batch=100):
        """Crawls concerts with no tracks in batches of 100 and
        populate their tracks in your db. Crawling tracks can take a
        long time (a few days) especially on low-performance
        machines. You may wish to run `Track.register()` in multiple
        python instances to crawl tracks concurrently. It is naively
        architected to avoid duplicates.

        usage:
        >>> from api.music import Track
        >>> Track.register()
        """
        while True:
            try:
                offset = randint(0, int(Concert.query.count() / batch))
                concerts = Concert.trackless_concerts(
                    limit=batch, offset=offset
                    )
                if not concerts:
                    break
                for concert in concerts:
                    print("%s CONCERT: %s" % ("*" * 10, concert.tag))
                    concert.register_tracks()
                    # remove concert if it still has no tracks after
                    # attempting to crawl.  (likely book / some other
                    # media accidentally include)
                    if not concert.tracks:
                        print("Removing %s" % concert.tag)
                        concert.remove()
            except (ObjectDeletedError, InvalidRequestError):
                db.remove()

    def dict(self):
        track = super(Track, self).dict()
        track['download'] = '%s/stream/%s/%s' % (
            Archive.BASE_URL, self.item_id, self.file_id)
        track['play'] = '%s/download/%s/%s' % (
            Archive.BASE_URL, self.item_id, self.file_id)
        track['artist'] = self.artist.dict()
        track['item_id'] = self.concert.tag
        return track

    @classmethod
    def search(cls, query, field, limit=10, page=0):
        return cls.query.filter(getattr(cls, field).ilike("%" + query + "%"))\
            .distinct(cls.artist_id).offset(page * limit).limit(limit).all()


class Sessions(core.Base):

    __tablename__ = "sessions"
    TBL = __tablename__

    session_id = Column(Unicode(40), primary_key=True)
    atime = Column(DateTime(timezone=False), default=datetime.utcnow,
                   nullable=False)
    data = Column(Unicode)

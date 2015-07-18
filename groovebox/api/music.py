#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    api/music.py
    ~~~~~~~~~~~~

    Groovebox Music API

    :copyright: (c) 2015 by mek.
    :license: see LICENSE for more details.
"""

from datetime import datetime
from api import DBSession, engine, core
from api.vendors import Crawler
from sqlalchemy import Column, Unicode, BigInteger, Integer, \
    DateTime, ForeignKey, ForeignKey, Table
from sqlalchemy.orm import deferred, relationship
from utils import time2sec

def coldstart(concerts=True, tracks=True, crawl=False):
    """Build tables, get artists and their concerts and insert
    into the database. If crawl is specified, retrieve tracks from
    each artist's concerts and then rebuild whoosh search index.
    
    usage:
        >>> from api.crawler import Worker;Worker.coldstart()
    """
    Track.metadata.create_all(engine) # create tables
    Artist.register(concerts=concerts, tracks=tracks) # populate db


artist_to_genre = \
    Table('artists_genres', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('artist_id', BigInteger, ForeignKey(
                'artists.id', use_alter=True), nullable=False),
          Column('genre_id', BigInteger, ForeignKey(
                'genres.id', use_alter=True), nullable=False)
          )


class Genre(core.Base):
    """Jazz, Classical, Funk, Jam, Reggae, Ambient, Blue"""

    __tablename__ = "genres"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    name = Column(Unicode, unique=True, nullable=False)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

class Artist(core.Base):

    __tablename__ = "artists"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    tag = Column(Unicode, unique=True, nullable=False)
    mbid = Column(Unicode, unique=True)
    name = Column(Unicode, nullable=False)
    avatar = Column(Unicode, default=u"")
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)
    genres = relationship('Genre', secondary=artist_to_genre,
                          backref="artist")

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
        concerts = Crawler.concerts(artist.tag)
        for concert in concerts:
            name = concerts['title']
            tag = concerts['identifier']
            print(concert)
            try:
                c = Concert(tag=tag, name=name)
                artist.concerts.append(c)
                artist.save()
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


    def dict(self, tracks=False):
        artist = super(Artist, self).dict()
        artist['tracks'] = [t.dict() for t in self.tracks]
        return artist


class Concert(core.Base):

    __tablename__ = "concerts"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    artist_id = Column(BigInteger, ForeignKey('artists.id'), nullable=False)
    tag = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                   nullable=False)    
    artist = relationship('Artist', backref='concerts') #lazy='dynamic')


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
                self.tracks.append(Track(
                        artist_id=self.artist_id,
                        concert_id=self.id,
                        item_id=concert.tag,
                        file_id=track['name'],
                        number=track['track'],
                        name=track['title'],
                        length=time2sec(track['length'])
                        ))
                self.save()
            except:
                pass


    def dict(self):
        concert = super(Concert, self).dict()
        concert['artist'] = self.artist.name
        concert['tracks'] = sorted([track.dict() for track in self.tracks],
                                   key=lambda x: x['number'])
        return concert


class Track(core.Base):

    __tablename__ = "tracks"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    artist_id = Column(BigInteger, ForeignKey('artists.id'), nullable=False)
    concert_id = Column(BigInteger, ForeignKey('concerts.id'), nullable=False)
    item_id = Column(Unicode, nullable=False)
    file_id = Column(Unicode, nullable=False)
    #song_id = Column(ForeignKey('songs.id'))
    number = Column(Integer, nullable=False)
    name = Column(Unicode)
    length = Column(Integer)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                   nullable=False)

    #song = relationship('Song')
    concert = relationship('Concert', backref='tracks')
    artist = relationship('Artist', backref='tracks')   


    def dict(self):
        track = super(Track, self).dict()
        track['artist'] = self.artist.name
        track['item_id'] = self.concert.tag
        return track


class Sessions(core.Base):

    __tablename__ = "sessions"
    TBL = __tablename__

    session_id = Column(Unicode(40), primary_key=True)
    atime = Column(DateTime(timezone=False), default=datetime.utcnow,
                   nullable=False)
    data = Column(Unicode)


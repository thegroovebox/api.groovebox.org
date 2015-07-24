groovebox
=========

.. image:: https://travis-ci.org/mekarpeles/groovebox.org.svg
    :target: https://travis-ci.org/mekarpeles/groovebox.org

A spotify-like media player for the Internet Archive's collection of live music.

Background
----------

Archive.org has an entire free Live Music collection consisting of
~150,000 live concerts, 2.5M tracks, and ~6,500+ artists. Currently,
there's no easy way to search individual tracks or play tracks from
different albums. Enter groovebox. Groovebox is a spotify clone for
the Internet Archive's music collection.

Installation
------------

The following instructions assume Ubuntu or Debian hosts:

.. code:: bash

    $ aptitude install postgresql-9.4
    $ git clone https://github.com/mekarpeles/groovebox.org.git
    $ cd groovebox.org
    $ pip3 install -e .
    $ cd groovebox
    $ python3.4 app.py # this runs the app

Create Database
---------------

.. code:: bash

    $ sudo -upostgres psql # connect to postgres

Change user and password below as desired:

.. code:: sql

    CREATE USER archivist WITH PASSWORD 'myPassword';
    CREATE DATABASE groovebox OWNER archivist;
    GRANT ALL PRIVILEGES ON DATABASE groovebox to archivist;

Configure App Settings
----------------------

Open `groovebox/configs/settings.cfg` and update the database settings
according to the credentials you choose in the previous step. An
example for the default credentials we used above might look like:

.. code:: python

    [server]
    host = 0.0.0.0
    port = 8080
    debug = 0

    [ssl]
    crt =
    key =

    [db]
    host = localhost
    user = archivist
    pw = myPassword
    dbn = postgres
    db = groovebox
    port = 5432


Populate Database
-----------------

I am in the process of dumping the production groovebox database to a
file and uploading it to my Archive.org account so others can download
it as a seed / import it dump directly into their database.

For now, you can use the built in Groovebox Crawler to populate your
own database. Running the coldstart method will populate your database
with ~6.5k music artists and their concerts. It will not retrieve any
tracks. You can use `Track.register()` to crawl concerts with no
tracks in batches of 100 and populate their tracks in your db:

.. code:: python

    >>> from api.music import coldstart
    >>> coldstart() # creates db, crawls artists + concerts
    >>> from api.music import Track
    >>> Track.register()

Crawling tracks with `Track.register()` can take a long time (a few
days) especially on low-performance machines. You may wish to run
`Track.register()` in multiple python instances to crawl tracks
concurrently.

Once Track crawling is finished, `Album` and `Song` entries can be
crawled per `Artist` from sources like musixmatch, musicbrainz, and
itunes. Be mindful that some Archive.org artists are obscure and are
likely to return incorrect results. I have been doing this process
manually, starting with Artists on Archive.org which have 50
recordings or more (as this seems like an naive indicator of
popularity).

.. code:: python

    >>> from api.music import Artist
    >>> [a.discography() for a in Artist.query.all()]

The final step is entity resolving Tracks against Songs. This is
currently incomplete (E.T.A 7/27). This entails taking every `Track`
for a given `Artist` in the database and attempting to match it with a
single `Song`. This way, search results can show unique `Song` and
then versions (`Track`) of that song for various artists, rather than
multiple `Track` by the same `Artist` having the same title.


Running in Production
---------------------

Groovebox, in production, uses nginx w/ uwsgi on a small Linode
instance. If anyone would like to setup a production version of
Groovebox, feel free to contact me at michael.karpeles@gmail.com.

Documentation
=============

REST Api
--------

Groovebox exposes REST API endpoints for various entities, including:

- /api/artists
- /api/albums
- /api/genres
- /api/concerts
- /api/songs
- /api/tracks

The HTTP behavior of each of these endpoints is defined in `groovebox/views/apis/__init__.py`. The corresponding entities/models which provide data to these methods are defined in the file `groovebox/api/music.py`. They are built on top SQLAlchemy, a Python ORM.

An additional endpoint is provided for search which returns artists
and songs which match the GET parameter `q`.

- /api/search?q=

Most of the entity models are intuitive, except albums v. concerts and
songs v. tracks which are easily confused. Archive.org structures
their data such that an `Artist` is a collection of one or more
`Concert` and a `Concert` contains one or more `Track`.

Archive.org has no knowledge of an artist's albums. As a result, an
Album and its Songs are constructed from 3rd party services. An
`Album` is a collection of one or more `Song`, whereas a `Concert` is
a collection of one or more `Track`. A `Track` is any recording of a
song. An `Artist` may (and likely) has multiple `Track` of the same
`Song`. A `Song` may be associated with multiple `Album` from
different `Artist`. Currently, there is no support for an `Album`
having multiple `Artist`.

Data Sources
------------

Songs are fetched from:

- Internet Archive (Archive.org)

Metadata is collected from:

- Archive.org
- Musicbrainz
- Musixmatch

Happy listening!

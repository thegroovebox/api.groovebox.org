groovebox
=========

A spotify-like media player for the Internet Archive's collection of live music.

## Installation

    $ pip install -e .
    $ cd groovebox
    $ python3.4

    >>> from api import Worker
    >>> Worker.coldstart()

`Worker.coldstart` performs three actions:

- `register_artists`
- `crawl`
- `index`

`Worker.register_artists` creates a `python shelve <https://docs.python.org/3/library/shelve.html>`_ in the `crawls` directory for each artist. By default (unless `concerts=False` is specified to `Worker.register_artists`), each artist's shelve (the artist's flatfile serialized db in the crawls dir) will be created having a `concerts` key whose value is a dictionary of the artist's concerts. E.g. of the contents of such an artist's shelve:

    {
        "concerts": {
            "eits2007-03-29.adk51tl.flac16": {},
            "eits2011-04-08.mk41_16bit": {},
            "eits2002-09-22.flac16": {},
            "eits2004-02-09.sbd.rob.shnf": {},
            ...
        }
    }

`Worker.register_artists` also creates a master index `@master` which
has a single key "artists" which maps to a list of archive.org artist
ids:

    {
        "artists": ['GratefulDead', ...]
    }

`Worker.crawl` iterates over every artist in the `@master` index,
opens up the artist's shelve, iterates over the artist's concerts, and
downloads the metadata for each of the concert's songs. The result is
the song is added to the artist's shelve under the specified concerts:

    {
        "concerts": {
            "jimiller2011-11-05.jmiller2011-11-05": {
                {
                    "concert": "jimiller2011-11-05.jmiller2011-11-05",
                    "album": "2011-11-05 - Woodlands Tavern",
                    "title": "Sugar Magnolia",
                    "track": "09",
                    "creator": "JiMiller Band",
                    "length": "06:03",
                    "name": "jmb2011-11-05t09.mp3"
                }
            }
        }
    }

`Worker.index` traverses the master shelf and then builds a Whoosh
search index out of every song of every concert of every artist, for
each artist. The Whoosh index is essentially an optimized list of
searchable songs with references to archive.org artist, concert, and
file ids.

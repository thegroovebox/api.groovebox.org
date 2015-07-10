import json
from .crawler import Crawler


def artists():
    """Retrieves list of artists from groovebox json file"""
    return json.load(open('static/data/artists.json', 'r'))


def concerts(artist=None, concert=None):
    """Retrieves list of concerts from groovebox json file"""
    shows = json.load(open('static/data/concerts.json', 'r'))
    if artist:
        if concert:
            return Crawler.concert(concert)
        return shows[artist]
    return concerts


def track_index(artist, concert, ts=None):
    """Constructs a dictionary of track names within this concert
    mapped to metadata.

    params:
        artist - the collection / Archive.org id of artist 
        files - the Archive.org metadata files for this concert / item
        ts - a pre-existing dictionary of tracks
    """    
    ts = ts or {}
    
    for track in Crawler.concert(concert)['tracks']:
        title = track.get('title')
        # If track title is already in tracks
        if title.lower() in [t.lower() for t in ts]:
            # If artist already exists for track
            if artist.lower() in [t.lower() for t in ts[title]]:
                ts[title][artist].append(track)
            else:
                ts[title][artist] = [track]
        else:
            ts[title] = {
                artist: [track]
                }
    return ts

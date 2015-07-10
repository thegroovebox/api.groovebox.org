import requests
import json

BASE_URL = "https://archive.org"
API_URL = "%s/advancedsearch.php" % BASE_URL
METADATA = "%s/metadata" % BASE_URL

def artists():
    return json.load(open('static/data/artists.json', 'r'))

def concerts(band, limit=20000):
    """Retrieves all the concerts (items) of a band.

    params:
        band - the collection id for this band (e.g. GratefulDead)
    """
    params = {
        "q": "collection:(%s)" % band,
        "fl[]": "identifier",
        "rows": limit,
        "output": "json"
        }
    return requests.get(API_URL, params=params).json()

def tracks(concert):
    """Returns a unique, ordered list of tracks from a concert"""
    tracks = set()
    


def tracks(concert, ts=None):
    """Constructs a dictionary of track names within this concert mapped to metadata

    params:
        concert - item id of this concert
        ts - allow pre-existing list of tracks
    """
    ts = ts or {}
    r = requests.get("%s/%s" % (METADATA, concert)).json()
    fs = r['files']
    collection = r.get("metadata", {}).get("collection", ["Unknown Artist"])[0]
    for f in fs:
        title = f.get("title")
        if title:
            if title in ts:
                if collection in ts[title]:
                    ts[title][collection].append(f)
                else:
                    ts[title][collection] = [f]
            else:
                ts[title] = {
                    collection: [f]
                    }
    return ts

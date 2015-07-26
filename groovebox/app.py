#!/usr/bin/env python
# -*-coding: utf-8 -*-

"""
    app.py
    ~~~~~~

    :copyright: (c) 2015 by Mek
    :license: see LICENSE for more details.
"""

from flask import Flask
from flask.ext.routing import router
import views
from views import endpoints
from configs import options
from flask.ext.cors import CORS

urls = ('/favicon.ico', views.Favicon,
        '', endpoints
        )

app = router(Flask(__name__), urls)
CORS(app, resources=r'*', allow_headers='Content-Type')

if __name__ == "__main__":
    app.run(**options)

#!/usr/bin/env pythonNone
#-*-coding: utf-8 -*-

"""
    app.py
    ~~~~~~
    

    :copyright: (c) 2015 by Anonymous
    :license: BSD, see LICENSE for more details.
"""

from flask import Flask
from flask.ext.routing import router
from views import apis
import views
from configs import options

urls = ('/partials/<path:partial>', views.Partial,
        #'/api', apis,
        '/<path:uri>', views.Base,
        '/', views.Base
        )
app = router(Flask(__name__), urls)

if __name__ == "__main__":
    app.run(**options)


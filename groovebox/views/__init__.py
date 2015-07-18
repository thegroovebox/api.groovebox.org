#!/usr/bin/env python
# -*-coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~~~~~

    :copyright: (c) 2015 by Mek Karpeles
    :license: see LICENSE for more details.
"""

import json
from bson import json_util
from flask import render_template, Response, send_from_directory
from flask.views import MethodView
from werkzeug import wrappers
from api import DBSession
from configs import approot

class Favicon(MethodView):
    def get(self):
         return ""# send_from_directory('%s/static' % approot, 'favicon.ico')

class Base(MethodView):
    def get(self, uri=None):
        template = "partials/%s.html" % (uri or "index")
        return render_template('base.html', template=template)

class Partial(MethodView):
    def get(self, partial):
        return render_template('partials/%s.html' % partial)

def rest_api(f):
    """Decorator to allow routes to return json"""
    def inner(*args, **kwargs):
        try:
            try:
                res = f(*args, **kwargs)
                if isinstance(res, wrappers.Response):
                    return res
                response = Response(json.dumps(res, default=json_util.default))
            except Exception as e:
                response = Response(json.dumps(str(e)))

            response.headers.add('Content-Type', 'application/json')
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        finally:
            DBSession.rollback()
            DBSession.remove()
    return inner

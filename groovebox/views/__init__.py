#!/usr/bin/env python
# -*-coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~~~~~

    :copyright: (c) 2015 by Mek Karpeles
    :license: see LICENSE for more details.
"""

import json
import traceback
import os.path
from werkzeug import wrappers
from flask import Response, request
from flask.views import MethodView
from utils import DatetimeEncoder
from api import db
from configs import DEBUG


class Favicon(MethodView):
    def get(self):
        return ""


def rest_api(f):
    """Decorator to allow routes to return json"""
    def inner(*args, **kwargs):
        try:
            try:
                res = f(*args, **kwargs)
                if isinstance(res, wrappers.Response):
                    return res
                response = Response(json.dumps(res, cls=DatetimeEncoder))
            except Exception as e:
                top = traceback.extract_stack()[-1]
                r = {"message": str(e)}
                if DEBUG:
                    r['error'] = ', '.join([type(e).__name__,
                                            os.path.basename(top[0]),
                                            str(top[1])
                                            ])
                response = Response(json.dumps(r))
            response.headers.add('Content-Type', 'application/json')
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        finally:
            db.rollback()
            db.remove()
    return inner


def paginate(limit=100, dump=lambda i, **opts: i.dict(**opts), **options):
    def outer(f):
        def inner(*args, **kwargs):
            _limit = min(request.args.get("limit", limit), limit)
            _offset = request.args.get("page", 0) * _limit
            query = f(*args, **kwargs)
            # could do count on query or return current limit + page
            items = query.limit(_limit).offset(_offset).all()
            return [dump(i, **options) for i in items]
        return inner
    return outer

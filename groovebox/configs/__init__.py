#!/usr/bin/env pythonNone
#-*-coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~~~~~
    Configs

    :copyright: (c) 2015 by Mek
    :license: see LICENSE for more details.
"""

import os
import sys
import types
import configparser
import logging

path = os.path.dirname(os.path.realpath(__file__))
approot = os.path.abspath(os.path.join(path, os.pardir))

#logging.basicConfig(level=logging.ERROR, filename='%s/error.log' % approot)

def errorlog(f):
    """Prints and logs errors without breaking program execution"""
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(str(e))
            logging.exception(f.__qualname__)
        return inner


def getdef(self, section, option, default_value):
    try:
        return self.get(section, option)
    except:
        return default_value

config = configparser.ConfigParser()
config.read('%s/settings.cfg' % path)
config.getdef = types.MethodType(getdef, config)

# SERVER
HOST = config.getdef("server", "host", '0.0.0.0')
PORT = int(config.getdef("server", "port", 8080))
DEBUG = bool(int(config.getdef("server", "debug", 1)))
CRT = config.getdef("ssl", "crt", '')
KEY = config.getdef("ssl", "key", '')
options = {'debug': DEBUG, 'host': HOST, 'port': PORT}
if CRT and KEY:
    options['ssl_context'] = (CRT, KEY)

# DATABASES
DB_URI = '%(dbn)s://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % {
    'dbn': config.getdef('db', 'dbn', 'postgres'),
    'port': config.getdef('db', 'port', '5433'),
    'host': config.getdef('db', 'host', ''),
    'user': config.getdef('db', 'user', ''),
    'pw': config.getdef('db', 'pw', ''),
    'db': config.getdef('db', 'db', '')
    }

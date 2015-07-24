#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    tests.test_groovebox
    ~~~~~~~~~~~~~~~~~~~~

    This module tests groovebox

    :copyright: (c) 2015 by Mek.
    :license: see LICENSE for more details.
"""

import os
import unittest
import tempfile
import app
from api import music, vendors

class TestGroovebox(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()

#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel
from flask.ext.gravatar import Gravatar

import conf

# Create Flask application
app = Flask(__name__)
app.debug = True

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = os.urandom(12)
app.config['SQLALCHEMY_DATABASE_URI'] = conf.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = set(['xml', 'opml'])


from flask.ext.babel import format_datetime
app.jinja_env.filters['datetime'] = format_datetime

TIME_ZONE = {
                "en": "US/Eastern",
                "fr": "Europe/Paris"
            }


def allowed_file(filename):
    """
    Check if the uploaded file is allowed.
    """
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

babel = Babel(app)

# Gravatar
gravatar = Gravatar(app, size=100, rating='g', default='retro',
                    force_default=False, use_ssl=False, base_url=None)

from pyaggr3g470r import views

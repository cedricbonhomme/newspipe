#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel
from flask.ext.babel import format_datetime

import conf

# Create Flask application
app = Flask(__name__)
app.debug = conf.WEBSERVER_DEBUG

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = getattr(conf, 'WEBSERVER_SECRET', None)
if not app.config['SECRET_KEY']:
    app.config['SECRET_KEY'] = os.urandom(12)
app.config['SQLALCHEMY_DATABASE_URI'] = conf.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

app.config['RECAPTCHA_USE_SSL'] = True
app.config['RECAPTCHA_PUBLIC_KEY'] = conf.RECAPTCHA_PUBLIC_KEY
app.config['RECAPTCHA_PRIVATE_KEY'] = conf.RECAPTCHA_PRIVATE_KEY

if conf.ON_HEROKU:
    from flask_sslify import SSLify
    sslify = SSLify(app)

ALLOWED_EXTENSIONS = set(['xml', 'opml', 'json'])

def allowed_file(filename):
    """
    Check if the uploaded file is allowed.
    """
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

babel = Babel(app)

app.jinja_env.filters['datetime'] = format_datetime

# Views
from flask.ext.restful import Api
api = Api(app)

from pyaggr3g470r import views

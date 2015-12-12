#! /usr/bin/env python
# -*- coding: utf-8 -

# required imports and code exection for basic functionning

import os
import conf
import logging
from urllib.parse import urlsplit

def set_logging(log_path, log_level=logging.INFO,
                log_format='%(asctime)s %(levelname)s %(message)s'):
    logger = logging.getLogger('jarr')
    formater = logging.Formatter(log_format)
    handler = logging.FileHandler(log_path)
    handler.setFormatter(formater)
    logger.addHandler(handler)
    logger.setLevel(log_level)

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# Create Flask application
application = Flask('web')
if os.environ.get('PYAGG_TESTING', False) == 'true':
    application.debug = logging.DEBUG
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    application.config['TESTING'] = True
else:
    application.debug = conf.LOG_LEVEL <= logging.DEBUG
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    application.config['SQLALCHEMY_DATABASE_URI'] \
            = conf.SQLALCHEMY_DATABASE_URI

scheme, domain, _, _, _ = urlsplit(conf.PLATFORM_URL)
application.config['SERVER_NAME'] = domain
application.config['PREFERRED_URL_SCHEME'] = scheme

set_logging(conf.LOG_PATH, log_level=conf.LOG_LEVEL)

# Create dummy secrey key so we can use sessions
application.config['SECRET_KEY'] = getattr(conf, 'WEBSERVER_SECRET', None)
if not application.config['SECRET_KEY']:
    application.config['SECRET_KEY'] = os.urandom(12)

application.config['RECAPTCHA_USE_SSL'] = True
application.config['RECAPTCHA_PUBLIC_KEY'] = conf.RECAPTCHA_PUBLIC_KEY
application.config['RECAPTCHA_PRIVATE_KEY'] = conf.RECAPTCHA_PRIVATE_KEY

db = SQLAlchemy(application)

def populate_g():
    from flask import g
    g.db = db
    g.app = application

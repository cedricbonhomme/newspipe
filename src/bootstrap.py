#! /usr/bin/env python
# -*- coding: utf-8 -

# required imports and code exection for basic functionning

import os
import conf
import logging
import flask_restless
from urllib.parse import urlsplit

def set_logging(log_path, log_level=logging.INFO,
                log_format='%(asctime)s %(levelname)s %(message)s'):
    formater = logging.Formatter(log_format)
    handler = logging.FileHandler(log_path)
    handler.setFormatter(formater)
    for logger_name in ('bootstrap', 'web', 'manager', 'runserver'):
        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)
        logger.setLevel(log_level)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create Flask application
application = Flask('web')
if os.environ.get('JARR_TESTING', False) == 'true':
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

# Create secrey key so we can use sessions
application.config['SECRET_KEY'] = getattr(conf, 'WEBSERVER_SECRET', None)
if not application.config['SECRET_KEY']:
    application.config['SECRET_KEY'] = os.urandom(12)

application.config['SECURITY_PASSWORD_SALT'] = getattr(conf,
                                                'SECURITY_PASSWORD_SALT', None)
if not application.config['SECURITY_PASSWORD_SALT']:
    application.config['SECURITY_PASSWORD_SALT'] = os.urandom(12)

db = SQLAlchemy(application)

# Create the Flask-Restless API manager.
manager = flask_restless.APIManager(application, flask_sqlalchemy_db=db)

def populate_g():
    from flask import g
    g.db = db
    g.app = application

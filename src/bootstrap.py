#! /usr/bin/env python
# -*- coding: utf-8 -

# required imports and code execution for basic functionning

import os
import conf
import logging
import flask_restless
from urllib.parse import urlsplit


def set_logging(log_path=None, log_level=logging.INFO, modules=(),
                log_format='%(asctime)s %(levelname)s %(message)s'):
    if not modules:
        modules = ('root', 'bootstrap', 'runserver',
                   'web', 'crawler.classic_crawler', 'manager', 'plugins')
    if conf.ON_HEROKU:
        log_format = '%(levelname)s %(message)s'
    if log_path:
        if not os.path.exists(os.path.dirname(log_path)):
            os.makedirs(os.path.dirname(log_path))
        if not os.path.exists(log_path):
            open(log_path, 'w').close()
        handler = logging.FileHandler(log_path)
    else:
        handler = logging.StreamHandler()
    formater = logging.Formatter(log_format)
    handler.setFormatter(formater)
    for logger_name in modules:
        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)
        for handler in logger.handlers:
            handler.setLevel(log_level)
        logger.setLevel(log_level)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create Flask application
application = Flask('web')
if os.environ.get('Newspipe_TESTING', False) == 'true':
    application.debug = logging.DEBUG
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    application.config['TESTING'] = True
else:
    application.debug = conf.LOG_LEVEL <= logging.DEBUG
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    application.config['SQLALCHEMY_DATABASE_URI'] \
            = conf.SQLALCHEMY_DATABASE_URI
    if 'postgres' in conf.SQLALCHEMY_DATABASE_URI:
        application.config['SQLALCHEMY_POOL_SIZE'] = 15
        application.config['SQLALCHEMY_MAX_OVERFLOW'] = 0

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

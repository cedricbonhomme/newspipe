#! /usr/bin/env python
#-*- coding: utf-8 -*-

""" Program variables.

This file contain the variables used by the application.
"""

import os, sys
try:
    import configparser as confparser
except:
    import ConfigParser as confparser
# load the configuration
config = confparser.SafeConfigParser()
config.read("./conf/conf.cfg")





basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5









PATH = os.path.abspath(".")

DATABASE_NAME = config.get('database', 'name')
DATABASE_PORT = int(config.get('database', 'port'))
DATABASE_USERNAME = config.get('database', 'username')
DATABASE_PASSWORD = config.get('database', 'password')
DATABASE_ADDRESS = config.get('database', 'address')

HTTP_PROXY = config.get('feedparser', 'http_proxy')
USER_AGENT = config.get('feedparser', 'user_agent')
RESOLVE_ARTICLE_URL = int(config.get('feedparser', 'resolve_article_url')) == 1

WEBSERVER_DEBUG = int(config.get('webserver', 'debug')) == 1
WEBSERVER_HOST = config.get('webserver', 'host')
WEBSERVER_PORT = int(config.get('webserver', 'port'))

MAIL_ENABLED = int(config.get('mail', 'enabled')) == 1
MAIL_HOST = config.get('mail', 'host')
MAIL_PORT = int(config.get('mail', 'port'))
MAIL_TLS = int(config.get('mail', 'tls')) == 1
MAIL_SSL = int(config.get('mail', 'ssl')) == 1
MAIL_USERNAME = config.get('mail', 'username')
MAIL_PASSWORD = config.get('mail', 'password')
MAIL_FROM = config.get('mail', 'mail_from')
MAIL_TO = config.get('mail', 'mail_to')

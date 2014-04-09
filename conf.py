#! /usr/bin/env python
#-*- coding: utf-8 -*-

""" Program variables.

This file contain the variables used by the application.
"""

import os, sys

ON_HEROKU = int(os.environ.get('HEROKU', 0)) == 1

if not ON_HEROKU:
    try:
        import configparser as confparser
    except:
        import ConfigParser as confparser
    # load the configuration
    config = confparser.SafeConfigParser()
    config.read("./conf/conf.cfg")

    # Whoosh does not work on Heroku
    WHOOSH_ENABLED = True

    SQLALCHEMY_DATABASE_URI = config.get('database', 'uri')

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

    basedir = os.path.abspath(os.path.dirname(__file__))
    PATH = os.path.abspath(".")

else:
    HTTP_PROXY = ""
    USER_AGENT = "pyAggr3g470r (https://bitbucket.org/cedricbonhomme/pyaggr3g470r)"
    RESOLVE_ARTICLE_URL = int(os.environ.get('RESOLVE_ARTICLE_URL', 0)) == 1

    WEBSERVER_DEBUG = False
    WEBSERVER_HOST ='0.0.0.0'
    WEBSERVER_PORT = int(os.environ.get('PORT', 5000))

    MAIL_ENABLED = False

    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

CSRF_ENABLED = True
# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

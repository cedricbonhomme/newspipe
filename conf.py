#! /usr/bin/env python
#-*- coding: utf-8 -*-

""" Program variables.

This file contain the variables used by the application.
"""

import os

basedir = os.path.abspath(os.path.dirname(__file__))
PATH = os.path.abspath(".")

# available languages
LANGUAGES = {
    'en': 'English',
    'fr': 'French'
}

TIME_ZONE = {
    "en": "US/Eastern",
    "fr": "Europe/Paris"
}

ON_HEROKU = int(os.environ.get('HEROKU', 0)) == 1

if not ON_HEROKU:
    try:
        import configparser as confparser
    except:
        import ConfigParser as confparser
    # load the configuration
    config = confparser.SafeConfigParser()
    config.read(os.path.join(basedir, "conf/conf.cfg"))

    PLATFORM_URL = config.get('misc', 'platform_url')
    ADMIN_EMAIL = config.get('misc', 'admin_email')
    RECAPTCHA_PUBLIC_KEY = config.get('misc', 'recaptcha_public_key')
    RECAPTCHA_PRIVATE_KEY = config.get('misc', 'recaptcha_private_key')
    LOG_PATH = config.get('misc', 'log_path')
    PYTHON = config.get('misc', 'python')

    WHOOSH_ENABLED = True

    SQLALCHEMY_DATABASE_URI = config.get('database', 'uri')

    HTTP_PROXY = config.get('feedparser', 'http_proxy')
    USER_AGENT = config.get('feedparser', 'user_agent')
    RESOLVE_ARTICLE_URL = int(config.get('feedparser', 'resolve_article_url')) == 1

    WEBSERVER_DEBUG = int(config.get('webserver', 'debug')) == 1
    WEBSERVER_HOST = config.get('webserver', 'host')
    WEBSERVER_PORT = int(config.get('webserver', 'port'))
    WEBSERVER_SECRET = config.get('webserver', 'secret')

    NOTIFICATION_EMAIL = config.get('notification', 'email')
    NOTIFICATION_HOST = config.get('notification', 'host')
    NOTIFICATION_PORT = int(config.get('notification', 'port'))
    NOTIFICATION_TLS = int(config.get('notification', 'tls')) == 1
    NOTIFICATION_SSL = int(config.get('notification', 'ssl')) == 1
    NOTIFICATION_USERNAME = config.get('notification', 'username')
    NOTIFICATION_PASSWORD = config.get('notification', 'password')

    WEBZINE_ROOT = PATH + "/pyaggr3g470r/var/export/"

else:
    PLATFORM_URL = os.environ.get('PLATFORM_URL', 'https://pyaggr3g470r.herokuapp.com/')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '')
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', '')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', '')
    LOG_PATH = os.environ.get('LOG_PATH', 'pyaggr3g470r.log')
    PYTHON = 'python'

    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

    HTTP_PROXY = ""
    USER_AGENT = "Mozilla/5.0 (X11; Debian; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0"
    RESOLVE_ARTICLE_URL = int(os.environ.get('RESOLVE_ARTICLE_URL', 0)) == 1

    WEBSERVER_DEBUG = False
    WEBSERVER_HOST = '0.0.0.0'
    WEBSERVER_PORT = int(os.environ.get('PORT', 5000))
    WEBSERVER_SECRET = os.environ.get('SECRET_KEY', None)

    NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL', '')
    POSTMARK_API_KEY = os.environ.get('POSTMARK_API_KEY', '')

    WEBZINE_ROOT = "/tmp/"


CSRF_ENABLED = True
# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

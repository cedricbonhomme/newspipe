#! /usr/bin/env python
#-*- coding: utf-8 -*-

""" Program variables.

This file contain the variables used by the application.
"""

import os, sys

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
    config.read("./conf/conf.cfg")

    PLATFORM_URL = config.get('misc', 'platform_url')
    ADMIN_PLATFORM_EMAIL = config.get('misc', 'admin_platform_email')
    RECAPTCHA_PUBLIC_KEY = config.get('misc', 'recaptcha_public_key')
    RECAPTCHA_PRIVATE_KEY = config.get('misc', 'recaptcha_private_key')

    WHOOSH_ENABLED = True

    SQLALCHEMY_DATABASE_URI = config.get('database', 'uri')

    HTTP_PROXY = config.get('feedparser', 'http_proxy')
    USER_AGENT = config.get('feedparser', 'user_agent')
    RESOLVE_ARTICLE_URL = int(config.get('feedparser', 'resolve_article_url')) == 1

    WEBSERVER_DEBUG = int(config.get('webserver', 'debug')) == 1
    WEBSERVER_HOST = config.get('webserver', 'host')
    WEBSERVER_PORT = int(config.get('webserver', 'port'))

    ADMIN_EMAIL = config.get('mail', 'admin_email')
    MAIL_ENABLED = int(config.get('mail', 'enabled')) == 1
    MAIL_HOST = config.get('mail', 'host')
    MAIL_PORT = int(config.get('mail', 'port'))
    MAIL_TLS = int(config.get('mail', 'tls')) == 1
    MAIL_SSL = int(config.get('mail', 'ssl')) == 1
    MAIL_USERNAME = config.get('mail', 'username')
    MAIL_PASSWORD = config.get('mail', 'password')
    
    WEBZINE_ROOT = PATH + "/pyaggr3g470r/var/export/"

else:
    PLATFORM_URL = os.environ.get('PLATFORM_URL', 'https://pyaggr3g470r.herokuapp.com/')
    ADMIN_PLATFORM_EMAIL = os.environ.get('ADMIN_PLATFORM_EMAIL', '')
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', '')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', '')
    
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

    HTTP_PROXY = ""
    USER_AGENT = "Mozilla/5.0 (X11; Debian; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0"
    RESOLVE_ARTICLE_URL = int(os.environ.get('RESOLVE_ARTICLE_URL', 0)) == 1

    WEBSERVER_DEBUG = False
    WEBSERVER_HOST = '0.0.0.0'
    WEBSERVER_PORT = int(os.environ.get('PORT', 5000))

    MAIL_ENABLED = True
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '')
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_SMTP_SERVER', '')
    MAILGUN_KEY = os.environ.get('MAILGUN_API_KEY', '')

    WEBZINE_ROOT = "/tmp/"


CSRF_ENABLED = True
# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

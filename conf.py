#! /usr/bin/env python
# -*- coding: utf-8 -*-
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
DEFAULTS = {"python": "/usr/bin/python3.4",
            "recaptcha_public_key": "",
            "recaptcha_private_key": "",
            "nb_worker": "100",
            "default_max_error": "3",
            "log_path": "pyaggr3g470r.log",
            "user_agent": "pyAggr3g470r "
                    "(https://bitbucket.org/cedricbonhomme/pyaggr3g470r)",
            "resolve_article_url": "false",
            "http_proxy": "",
            "debug": "true",
            "secret": "",
            "enabled": "false",
            "email": "",
            "tls": "false",
            "ssl": "true",
            "host": "0.0.0.0",
            "port": "5000",
            "crawling_method": "classic",
            }

if not ON_HEROKU:
    try:
        import configparser as confparser
    except:
        import ConfigParser as confparser
    # load the configuration
    config = confparser.SafeConfigParser(defaults=DEFAULTS)
    config.read(os.path.join(basedir, "conf/conf.cfg"))

    PLATFORM_URL = config.get('misc', 'platform_url')
    ADMIN_EMAIL = config.get('misc', 'admin_email')
    RECAPTCHA_PUBLIC_KEY = config.get('misc', 'recaptcha_public_key')
    RECAPTCHA_PRIVATE_KEY = config.get('misc',
                                       'recaptcha_private_key')
    LOG_PATH = config.get('misc', 'log_path')
    PYTHON = config.get('misc', 'python')
    NB_WORKER = config.getint('misc', 'nb_worker')

    WHOOSH_ENABLED = True

    SQLALCHEMY_DATABASE_URI = config.get('database', 'uri')

    HTTP_PROXY = config.get('feedparser', 'http_proxy')
    USER_AGENT = config.get('feedparser', 'user_agent')
    RESOLVE_ARTICLE_URL = config.getboolean('feedparser',
                                            'resolve_article_url')
    DEFAULT_MAX_ERROR = config.getint('feedparser',
                                      'default_max_error')
    CRAWLING_METHOD = config.get('feedparser', 'crawling_method')

    WEBSERVER_DEBUG = config.getboolean('webserver', 'debug')
    WEBSERVER_HOST = config.get('webserver', 'host')
    WEBSERVER_PORT = config.getint('webserver', 'port')
    WEBSERVER_SECRET = config.get('webserver', 'secret')

    NOTIFICATION_EMAIL = config.get('notification', 'email')
    NOTIFICATION_HOST = config.get('notification', 'host')
    NOTIFICATION_PORT = config.getint('notification', 'port')
    NOTIFICATION_TLS = config.getboolean('notification', 'tls')
    NOTIFICATION_SSL = config.getboolean('notification', 'ssl')
    NOTIFICATION_USERNAME = config.get('notification', 'username')
    NOTIFICATION_PASSWORD = config.get('notification', 'password')

    WEBZINE_ROOT = PATH + "/pyaggr3g470r/var/export/"

else:
    PLATFORM_URL = os.environ.get('PLATFORM_URL',
            'https://pyaggr3g470r.herokuapp.com/')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '')
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', '')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', '')
    LOG_PATH = os.environ.get('LOG_PATH', 'pyaggr3g470r.log')
    PYTHON = 'python'

    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

    HTTP_PROXY = ""
    USER_AGENT = "Mozilla/5.0 " \
            "(X11; Debian; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0"
    RESOLVE_ARTICLE_URL = int(os.environ.get('RESOLVE_ARTICLE_URL', 0)) == 1
    DEFAULT_MAX_ERROR = int(os.environ.get('DEFAULT_MAX_ERROR', 6))
    CRAWLING_METHOD = os.environ.get('CRAWLING_METHOD',
                                     DEFAULTS['crawling_method'])

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

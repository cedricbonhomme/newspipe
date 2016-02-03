#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Program variables.

This file contain the variables used by the application.
"""
import os
import logging

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
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
DEFAULTS = {"platform_url": "https://JARR.herokuapp.com/",
            "cdn_address": "",
            "admin_email": "root@jarr.localhost",
            "postmark_api_key": "",
            "recaptcha_public_key": "",
            "recaptcha_private_key": "",
            "nb_worker": "100",
            "api_login": "",
            "api_passwd": "",
            "default_max_error": "3",
            "log_path": "jarr.log",
            "log_level": "info",
            "user_agent": "JARR (https://github.com/JARR-aggregator)",
            "resolve_article_url": "false",
            "http_proxy": "",
            "secret": "",
            "enabled": "false",
            "notification_email": "jarr@no-reply.com",
            "tls": "false",
            "ssl": "true",
            "host": "0.0.0.0",
            "port": "5000",
            "crawling_method": "classic",
            "webzine_root": "/tmp",
            }

if not ON_HEROKU:
    try:
        import configparser as confparser
    except:
        import ConfigParser as confparser
    # load the configuration
    config = confparser.SafeConfigParser(defaults=DEFAULTS)
    config.read(os.path.join(BASE_DIR, "conf/conf.cfg"))
else:
    class Config(object):
        def get(self, _, name):
            return os.environ.get(name.upper(), DEFAULTS.get(name))

        def getint(self, _, name):
            return int(self.get(_, name))

        def getboolean(self, _, name):
            value = self.get(_, name)
            if value == 'true':
                return True
            elif value == 'false':
                return False
            return None
    config = Config()


PLATFORM_URL = config.get('misc', 'platform_url')
ADMIN_EMAIL = config.get('misc', 'admin_email')
RECAPTCHA_PUBLIC_KEY = config.get('misc', 'recaptcha_public_key')
RECAPTCHA_PRIVATE_KEY = config.get('misc',
                                    'recaptcha_private_key')
LOG_PATH = os.path.abspath(config.get('misc', 'log_path'))
NB_WORKER = config.getint('misc', 'nb_worker')
API_LOGIN = config.get('crawler', 'api_login')
API_PASSWD = config.get('crawler', 'api_passwd')

WHOOSH_ENABLED = True

SQLALCHEMY_DATABASE_URI = config.get('database', 'database_url')

HTTP_PROXY = config.get('crawler', 'http_proxy')
USER_AGENT = config.get('crawler', 'user_agent')
RESOLVE_ARTICLE_URL = config.getboolean('crawler',
                                        'resolve_article_url')
DEFAULT_MAX_ERROR = config.getint('crawler',
                                  'default_max_error')
ERROR_THRESHOLD = int(DEFAULT_MAX_ERROR / 2)

CRAWLING_METHOD = config.get('crawler', 'crawling_method')

LOG_LEVEL = {'debug': logging.DEBUG,
             'info': logging.INFO,
             'warn': logging.WARN,
             'error': logging.ERROR,
             'fatal': logging.FATAL}[config.get('misc', 'log_level')]

WEBSERVER_HOST = config.get('webserver', 'host')
WEBSERVER_PORT = config.getint('webserver', 'port')
WEBSERVER_SECRET = config.get('webserver', 'secret')

CDN_ADDRESS = config.get('cdn', 'cdn_address')

NOTIFICATION_EMAIL = config.get('notification', 'notification_email')
NOTIFICATION_HOST = config.get('notification', 'host')
NOTIFICATION_PORT = config.getint('notification', 'port')
NOTIFICATION_TLS = config.getboolean('notification', 'tls')
NOTIFICATION_SSL = config.getboolean('notification', 'ssl')
NOTIFICATION_USERNAME = config.get('notification', 'username')
NOTIFICATION_PASSWORD = config.get('notification', 'password')
POSTMARK_API_KEY = config.get('notification', 'postmark_api_key')

WEBZINE_ROOT = config.get('webserver', 'webzine_root')

CSRF_ENABLED = True
# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

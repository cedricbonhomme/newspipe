#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Program variables.

This file contain the variables used by the application.
"""
import configparser as confparser
import os
import logging

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PATH = os.path.abspath(".")


# available languages
LANGUAGES = {"en": "English", "fr": "French"}

TIME_ZONE = {"en": "US/Eastern", "fr": "Europe/Paris"}

DEFAULTS = {
    "platform_url": "https://www.newspipe.org/",
    "self_registration": "false",
    "cdn_address": "",
    "admin_email": "info@newspipe.org",
    "token_validity_period": "3600",
    "default_max_error": "3",
    "log_path": "newspipe.log",
    "log_level": "info",
    "secret_key": "",
    "security_password_salt": "",
    "enabled": "false",
    "notification_email": "info@newspipe.org",
    "tls": "false",
    "ssl": "true",
    "host": "0.0.0.0",
    "port": "5000",
    "crawling_method": "default",
    "crawler_user_agent": "Newspipe (https://github.com/newspipe)",
    "crawler_timeout": "30",
    "crawler_resolv": "false",
    "feed_refresh_interval": "120",
}


# load the configuration
config = confparser.SafeConfigParser(defaults=DEFAULTS)
config.read(os.path.join(BASE_DIR, "conf/conf.cfg"))


WEBSERVER_HOST = config.get("webserver", "host")
WEBSERVER_PORT = config.getint("webserver", "port")
WEBSERVER_SECRET = config.get("webserver", "secret_key")
WEBSERVER_DEBUG = config.getboolean("webserver", "debug")

CDN_ADDRESS = config.get("cdn", "cdn_address")

try:
    PLATFORM_URL = config.get("misc", "platform_url")
except:
    PLATFORM_URL = "https://www.newspipe.org/"
ADMIN_EMAIL = config.get("misc", "admin_email")
SELF_REGISTRATION = config.getboolean("misc", "self_registration")
SECURITY_PASSWORD_SALT = config.get("misc", "security_password_salt")
try:
    TOKEN_VALIDITY_PERIOD = config.getint("misc", "token_validity_period")
except:
    TOKEN_VALIDITY_PERIOD = int(config.get("misc", "token_validity_period"))
LOG_PATH = os.path.abspath(config.get("misc", "log_path"))
LOG_LEVEL = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARN,
    "error": logging.ERROR,
    "fatal": logging.FATAL,
}[config.get("misc", "log_level")]

SQLALCHEMY_DATABASE_URI = config.get("database", "database_url")

CRAWLING_METHOD = config.get("crawler", "crawling_method")
CRAWLER_USER_AGENT = config.get("crawler", "user_agent")
DEFAULT_MAX_ERROR = config.getint("crawler", "default_max_error")
ERROR_THRESHOLD = int(DEFAULT_MAX_ERROR / 2)
CRAWLER_TIMEOUT = config.get("crawler", "timeout")
CRAWLER_RESOLV = config.getboolean("crawler", "resolv")
try:
    FEED_REFRESH_INTERVAL = config.getint("crawler", "feed_refresh_interval")
except:
    FEED_REFRESH_INTERVAL = int(config.get("crawler", "feed_refresh_interval"))

NOTIFICATION_EMAIL = config.get("notification", "notification_email")
NOTIFICATION_HOST = config.get("notification", "host")
NOTIFICATION_PORT = config.getint("notification", "port")
NOTIFICATION_TLS = config.getboolean("notification", "tls")
NOTIFICATION_SSL = config.getboolean("notification", "ssl")
NOTIFICATION_USERNAME = config.get("notification", "username")
NOTIFICATION_PASSWORD = config.get("notification", "password")

CSRF_ENABLED = True
# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

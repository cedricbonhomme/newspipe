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

PATH = os.path.abspath(".")

DATABASE_NAME = config.get('database', 'name')
DATABASE_PORT = int(config.get('database', 'port'))
DATABASE_USERNAME = config.get('database', 'username')
DATABASE_PASSWORD = config.get('database', 'password')
DATABASE_ADDRESS = config.get('database', 'address')

WEBSERVER_DEBUG = int(config.get('webserver', 'debug')) == 1
WEBSERVER_HOST = config.get('webserver', 'host')
WEBSERVER_PORT = int(config.get('webserver', 'port'))

MAIL_HOST = config.get('mail', 'host')
MAIL_PORT = int(config.get('mail', 'port'))
MAIL_SSL = int(config.get('mail', 'ssl')) == 1
MAIL_USERNAME = config.get('mail', 'username')

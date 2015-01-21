# required imports and code exection for basic functionning

import os
import sys
if 'threading' in sys.modules:
    raise Exception('threading module loaded before patching!')
import conf
import logging

if not (conf.WEBSERVER_DEBUG or conf.ON_HEROKU):
    import gevent.monkey
    gevent.monkey.patch_thread()


def set_logging(log_path, log_level=logging.INFO,
                log_format='%(asctime)s %(levelname)s %(message)s'):
    logger = logging.getLogger('pyaggr3g470r')
    formater = logging.Formatter(log_format)
    handler = logging.FileHandler(log_path)
    handler.setFormatter(formater)
    logger.addHandler(handler)
    logger.setLevel(log_level)

set_logging(conf.LOG_PATH)

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# Create Flask application
application = Flask('pyaggr3g470r')
application.debug = conf.WEBSERVER_DEBUG

# Create dummy secrey key so we can use sessions
application.config['SECRET_KEY'] = getattr(conf, 'WEBSERVER_SECRET', None)
if not application.config['SECRET_KEY']:
    application.config['SECRET_KEY'] = os.urandom(12)
application.config['SQLALCHEMY_DATABASE_URI'] = conf.SQLALCHEMY_DATABASE_URI

application.config['RECAPTCHA_USE_SSL'] = True
application.config['RECAPTCHA_PUBLIC_KEY'] = conf.RECAPTCHA_PUBLIC_KEY
application.config['RECAPTCHA_PRIVATE_KEY'] = conf.RECAPTCHA_PRIVATE_KEY

db = SQLAlchemy(application)

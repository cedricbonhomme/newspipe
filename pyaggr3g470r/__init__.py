#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flask import Flask
from flask.ext.mongoengine import MongoEngine

import conf
from models import *

# Create Flask application
app = Flask(__name__)
app.debug = True

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = os.urandom(12)

app.config['MONGODB_SETTINGS'] = {'DB': conf.DATABASE_NAME}
app.config["MAIL_SERVER"] = conf.MAIL_HOST
app.config["MAIL_PORT"] = conf.MAIL_PORT
app.config["MAIL_USE_SSL"] = conf.MAIL_SSL
app.config["MAIL_USERNAME"] = conf.MAIL_USERNAME
#app.config["MAIL_PASSWORD"] = 'your-password'

# Initializes the database
db = MongoEngine(app)
db.init_app(app)

from views import mail
mail.init_app(app)

from pyaggr3g470r import views
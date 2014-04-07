#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import conf

# Create Flask application
app = Flask(__name__)
app.debug = True

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = os.urandom(12)
app.config['SQLALCHEMY_DATABASE_URI'] = conf.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

app.config["MAIL_SERVER"] = conf.MAIL_HOST
app.config["MAIL_PORT"] = conf.MAIL_PORT
app.config["MAIL_USE_TLS"] = conf.MAIL_TLS
app.config["MAIL_USE_SSL"] = conf.MAIL_SSL
app.config["MAIL_USERNAME"] = conf.MAIL_USERNAME
app.config["MAIL_PASSWORD"] = conf.MAIL_PASSWORD

from flask.ext.mail import Message, Mail
mail = Mail(app)

from pyaggr3g470r import views
#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flask import Flask, session, g
from flask.ext.mongoengine import MongoEngine
#from flask.ext.login import AnonymousUserMixin

from flask.ext.admin import Admin
from flask.ext.admin.contrib.mongoengine import ModelView
from flask_debugtoolbar import DebugToolbarExtension

import conf
from models import *

# Create Flask applicatio
app = Flask(__name__)
app.debug = True

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = conf.WEBSERVER_SECRETKEY

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

# For Flask-DebugToolbar
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

# Administration panel
admin = Admin(app, name='pyAggr3g470r')
# Add administrative views here
class FeedView(ModelView):
    column_filters = ['title', 'link']

    column_searchable_list = ('title', 'link')

    form_ajax_refs = {
        'tags': {
            'fields': ('title', 'link')
        }
    }
class ArticleView(ModelView):
    column_filters = ['title', 'link']

    column_searchable_list = ('title', 'link')

    form_ajax_refs = {
        'tags': {
            'fields': ('title', 'link')
        }
    }
admin.add_view(FeedView(Feed))
admin.add_view(ArticleView(Article))


from pyaggr3g470r import views

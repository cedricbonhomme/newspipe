#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flask import Flask, session, g
from flask.ext.mongoengine import MongoEngine

from flask.ext.admin import Admin
from flask.ext.admin.contrib.mongoengine import ModelView

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

# Administration panel
admin = Admin(app, name='pyAggr3g470r')
# Add administrative views here
class UserView(ModelView):
    form_subdocuments = {
        'feeds': {
            'form_columns': ('title', 'link')
        }
    }
class FeedView(ModelView):
    column_filters = ['title', 'link']

    column_searchable_list = ('title', 'link')
class ArticleView(ModelView):
    column_filters = ['title', 'link']

    column_searchable_list = ('title', 'link')
#admin.add_view(UserView(User))
admin.add_view(FeedView(Feed))
admin.add_view(ArticleView(Article))


from pyaggr3g470r import views
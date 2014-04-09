#! /usr/bin/env python
# -*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2013  Cédric Bonhomme - http://cedricbonhomme.org/
#
# For more information : http://bitbucket.org/cedricbonhomme/pyaggr3g470r/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.3 $"
__date__ = "$Date: 2013/11/05 $"
__revision__ = "$Date: 2013/11/16 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

from datetime import datetime
from sqlalchemy import desc
from werkzeug import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from pyaggr3g470r import db

class User(db.Model, UserMixin):
    """
    Represent a user.
    """
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String())
    lastname = db.Column(db.String())
    email = db.Column(db.String(), index = True, unique = True)
    pwdhash = db.Column(db.String())
    roles = db.relationship('Role', backref = 'user', lazy = 'dynamic')
    date_created = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.now)
    feeds = db.relationship('Feed', backref = 'subscriber', lazy = 'dynamic', cascade='all,delete-orphan')

    def get_id(self):
        """
        Return the id (email) of the user.
        """
        return self.email

    def set_password(self, password):
        """
        Hash the password of the user.
        """
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check the password of the user.
        """
        return check_password_hash(self.pwdhash, password)

    def is_admin(self):
        """
        Return True if the user has administrator rights.
        """
        return len([role for role in self.roles if role.name == "admin"]) != 0

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return '<User %r>' % (self.firstname)

class Role(db.Model):
    """
    Represent a role.
    """
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), unique = True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Feed(db.Model):
    """
    Represent a station.
    """
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(), default="New station")
    description = db.Column(db.String(), default="FR")
    link = db.Column(db.String())
    site_link = db.Column(db.String(), default="New station")
    email_notification = db.Column(db.Boolean(), default=False)
    enabled = db.Column(db.Boolean(), default=True)
    created_date = db.Column(db.DateTime(), default=datetime.now)
    articles = db.relationship('Article', backref = 'source', lazy = 'dynamic', cascade='all,delete-orphan',
                                order_by=desc("Article.date"))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Feed %r>' % (self.title)

class Article(db.Model):
    """
    Represent an article from a feed.
    """
    id = db.Column(db.Integer, primary_key = True)
    link = db.Column(db.String())
    title = db.Column(db.String())
    content = db.Column(db.String())
    readed = db.Column(db.Boolean(), default=False)
    like = db.Column(db.Boolean(), default=False)
    date = db.Column(db.DateTime(), default=datetime.now)
    retrieved_date = db.Column(db.DateTime(), default=datetime.now)

    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'))

    def __repr__(self):
        return '<Article %r>' % (self.title)

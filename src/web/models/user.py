#! /usr/bin/env python
# -*- coding: utf-8 -*-

# newspipe - A Web based news aggregator.
# Copyright (C) 2010-2018  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : https://github.com/newspipe/newspipe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.4 $"
__date__ = "$Date: 2013/11/05 $"
__revision__ = "$Date: 2014/04/12 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

import re
import random
import hashlib
from datetime import datetime
from werkzeug import check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import validates

from bootstrap import db
from web.models.right_mixin import RightMixin
from web.models.category import Category
from web.models.feed import Feed


class User(db.Model, UserMixin, RightMixin):
    """
    Represent a user.
    """
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(), unique=True)
    pwdhash = db.Column(db.String())

    automatic_crawling = db.Column(db.Boolean(), default=True)

    is_public_profile = db.Column(db.Boolean(), default=False)
    bio = db.Column(db.String(5000), default="")
    webpage = db.Column(db.String(), default="")
    twitter = db.Column(db.String(), default="")

    date_created = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    # user rights
    is_active = db.Column(db.Boolean(), default=False)
    is_admin = db.Column(db.Boolean(), default=False)
    is_api = db.Column(db.Boolean(), default=False)

    # relationships
    categories = db.relationship('Category', backref='user',
                              cascade='all, delete-orphan',
                            foreign_keys=[Category.user_id])
    feeds = db.relationship('Feed', backref='user',
                         cascade='all, delete-orphan',
                            foreign_keys=[Feed.user_id])

    @staticmethod
    def _fields_base_write():
        return {'login', 'password'}

    @staticmethod
    def _fields_base_read():
        return {'date_created', 'last_connection'}

    @staticmethod
    def make_valid_nickname(nickname):
        return re.sub('[^a-zA-Z0-9_\.]', '', nickname)

    @validates('bio')
    def validates_bio(self, key, value):
        assert len(value) <= 5000, \
                AssertionError("maximum length for bio: 5000")
        return value.strip()

    def get_id(self):
        """
        Return the id of the user.
        """
        return self.id

    def check_password(self, password):
        """
        Check the password of the user.
        """
        return check_password_hash(self.pwdhash, password)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return '<User %r>' % (self.nickname)

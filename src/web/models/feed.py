#! /usr/bin/env python
# -*- coding: utf-8 -*-

# newspipe - A Web based news aggregator.
# Copyright (C) 2010-2016  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : https://github.com/Newspipe/Newspipe
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

from bootstrap import db
from datetime import datetime
from sqlalchemy import desc, Index
from sqlalchemy.orm import validates
from web.models.right_mixin import RightMixin
from web.models.article import Article


class Feed(db.Model, RightMixin):
    """
    Represent a feed.
    """
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(), default="")
    description = db.Column(db.String(), default="FR")
    link = db.Column(db.String(), nullable=False)
    site_link = db.Column(db.String(), default="")
    enabled = db.Column(db.Boolean(), default=True)
    created_date = db.Column(db.DateTime(), default=datetime.utcnow)
    filters = db.Column(db.PickleType, default=[])
    private = db.Column(db.Boolean(), default=False)

    # cache handling
    etag = db.Column(db.String(), default="")
    last_modified = db.Column(db.String(), default="")
    last_retrieved = db.Column(db.DateTime(), default=datetime(1970, 1, 1))

    # error logging
    last_error = db.Column(db.String(), default="")
    error_count = db.Column(db.Integer(), default=0)

    # relationship
    icon_url = db.Column(db.String(), db.ForeignKey('icon.url'), default=None)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer(), db.ForeignKey('category.id'))
    articles = db.relationship(Article, backref='source', lazy='dynamic',
                               cascade='all,delete-orphan',
                               order_by=desc(Article.date))

    # index
    idx_feed_uid_cid = Index('user_id', 'category_id')
    idx_feed_uid = Index('user_id')

     # api whitelists
    @staticmethod
    def _fields_base_write():
        return {'title', 'description', 'link', 'site_link', 'enabled',
                'filters', 'last_error', 'error_count', 'category_id'}

    @staticmethod
    def _fields_base_read():
        return {'id', 'user_id', 'icon_url', 'last_retrieved'}

    @validates('title')
    def validates_title(self, key, value):
        return str(value).strip()

    @validates('description')
    def validates_description(self, key, value):
        return str(value).strip()

    def __repr__(self):
        return '<Feed %r>' % (self.title)

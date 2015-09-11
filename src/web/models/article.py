#! /usr/bin/env python
# -*- coding: utf-8 -*-

# jarr - A Web based news aggregator.
# Copyright (C) 2010-2015  Cédric Bonhomme - https://www.JARR-aggregator.org
#
# For more information : https://github.com/JARR-aggregator/JARR
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
from sqlalchemy import asc, desc


class Article(db.Model):
    "Represent an article from a feed."
    id = db.Column(db.Integer(), primary_key=True)
    entry_id = db.Column(db.String())
    link = db.Column(db.String())
    title = db.Column(db.String())
    content = db.Column(db.String())
    readed = db.Column(db.Boolean(), default=False)
    like = db.Column(db.Boolean(), default=False)
    #notes = db.Column(db.String(), default="")
    date = db.Column(db.DateTime(), default=datetime.now)
    retrieved_date = db.Column(db.DateTime(), default=datetime.now)

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    feed_id = db.Column(db.Integer(), db.ForeignKey('feed.id'))
    category_id = db.Column(db.Integer(), db.ForeignKey('category.id'))

    def previous_article(self):
        """
        Returns the previous article (older).
        """
        return Article.query.filter(Article.date < self.date,
                                    Article.feed_id == self.feed_id)\
                            .order_by(desc("Article.date")).first()

    def next_article(self):
        """
        Returns the next article (newer).
        """
        return Article.query.filter(Article.date > self.date,
                                    Article.feed_id == self.feed_id)\
                            .order_by(asc("Article.date")).first()

    def __repr__(self):
        return "<Article(id=%d, entry_id=%s, title=%r, " \
               "date=%r, retrieved_date=%r)>" % (self.id, self.entry_id,
                       self.title, self.date, self.retrieved_date)

    def dump(self):
        return {"id": self.id,
                "user_id": self.user_id,
                "entry_id": self.entry_id,
                "title": self.title,
                "link": self.link,
                "content": self.content,
                "readed": self.readed,
                "like": self.like,
                "date": self.date,
                "retrieved_date": self.retrieved_date,
                "feed_id": getattr(self.source, 'id', None),
                "feed_name": getattr(self.source, 'title', None)}

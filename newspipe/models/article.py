#! /usr/bin/env python
# Newspipe - A web news aggregator.
# Copyright (C) 2010-2024 Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information: https://sr.ht/~cedric/newspipe
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
__version__ = "$Revision: 0.5 $"
__date__ = "$Date: 2013/11/05 $"
__revision__ = "$Date: 2016/10/04 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

from datetime import datetime

# from sqlalchemy import Index, ForeignKeyConstraint
from sqlalchemy.ext.associationproxy import association_proxy

from newspipe.bootstrap import db
from newspipe.models.right_mixin import RightMixin


class Article(db.Model, RightMixin):
    "Represent an article from a feed."
    id = db.Column(db.Integer(), primary_key=True)
    entry_id = db.Column(db.String(), nullable=False)
    link = db.Column(db.String())
    title = db.Column(db.String())
    content = db.Column(db.String())
    readed = db.Column(db.Boolean(), default=False)
    like = db.Column(db.Boolean(), default=False)
    date = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_date = db.Column(db.DateTime(), default=datetime.utcnow)
    retrieved_date = db.Column(db.DateTime(), default=datetime.utcnow)

    # foreign keys
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    feed_id = db.Column(db.Integer(), db.ForeignKey("feed.id"))
    category_id = db.Column(db.Integer(), db.ForeignKey("category.id"), nullable=True)

    # relationships
    tag_objs = db.relationship(
        "ArticleTag",
        back_populates="article",
        cascade="all,delete-orphan",
        lazy=False,
        foreign_keys="[ArticleTag.article_id]",
    )
    tags = association_proxy("tag_objs", "text")

    # __table_args__ = (
    #     ForeignKeyConstraint([user_id], ["user.id"], ondelete="CASCADE"),
    #     ForeignKeyConstraint([feed_id], ["feed.id"], ondelete="CASCADE"),
    #     ForeignKeyConstraint([category_id], ["category.id"], ondelete="CASCADE"),
    #     Index("ix_article_eid_cid_uid", user_id, category_id, entry_id),
    #     Index("ix_article_retrdate", retrieved_date),
    #     Index("user_id"),
    #     Index("user_id", "category_id"),
    #     Index("user_id", "feed_id"),
    #     Index("ix_article_uid_fid_eid", user_id, feed_id, entry_id),
    # )

    # api whitelists
    @staticmethod
    def _fields_base_write():
        return {"readed", "like", "feed_id", "category_id"}

    @staticmethod
    def _fields_base_read():
        return {
            "id",
            "entry_id",
            "link",
            "title",
            "content",
            "date",
            "retrieved_date",
            "user_id",
            "tags",
        }

    @staticmethod
    def _fields_api_write():
        return {"tags"}

    def __repr__(self):
        return (
            "<Article(id=%d, entry_id=%s, title=%r, "
            "date=%r, retrieved_date=%r)>"
            % (self.id, self.entry_id, self.title, self.date, self.retrieved_date)
        )

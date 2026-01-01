#! /usr/bin/env python
# Newspipe - A web news aggregator.
# Copyright (C) 2010-2026 Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information: https://github.com/cedricbonhomme/newspipe
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

from datetime import datetime

from sqlalchemy import ForeignKeyConstraint, Index, desc
from sqlalchemy.orm import validates

from newspipe.bootstrap import db
from newspipe.lib.sanitizers import sanitize_text
from newspipe.models.article import Article
from newspipe.models.right_mixin import RightMixin


class Feed(db.Model, RightMixin):  # type: ignore[name-defined]
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

    # foreign keys
    icon_url = db.Column(db.String(), db.ForeignKey("icon.url"), default=None)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    category_id = db.Column(db.Integer(), db.ForeignKey("category.id"), nullable=True)

    # relationship
    articles = db.relationship(
        Article,
        backref="source",
        lazy="dynamic",
        cascade="all,delete-orphan",
        order_by=desc(Article.date),
    )

    __table_args__ = (
        ForeignKeyConstraint([user_id], ["user.id"], ondelete="CASCADE"),
        ForeignKeyConstraint([category_id], ["category.id"], ondelete="CASCADE"),
        ForeignKeyConstraint([icon_url], ["icon.url"]),
        Index("ix_feed_uid", user_id),
        Index("ix_feed_uid_cid", user_id, category_id),
    )

    # idx_feed_uid_cid = Index("user_id", "category_id")
    # idx_feed_uid = Index("user_id")

    # api whitelists
    @staticmethod
    def _fields_base_write():
        return {
            "title",
            "description",
            "link",
            "site_link",
            "enabled",
            "filters",
            "last_error",
            "error_count",
            "category_id",
        }

    @staticmethod
    def _fields_base_read():
        return {"id", "user_id", "icon_url", "last_retrieved"}

    @validates("title")
    def validates_title(self, key, value):
        value = value.strip()
        cleaned = sanitize_text(value)
        return cleaned

    @validates("description")
    def validates_description(self, key, value):
        value = value.strip()
        cleaned = sanitize_text(value)
        return cleaned

    def __repr__(self):
        return "<Feed %r>" % (self.title)

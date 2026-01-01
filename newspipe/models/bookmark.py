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
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2016/12/07 $"
__revision__ = "$Date: 2016/12/07 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

from datetime import datetime

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

from newspipe.bootstrap import db
from newspipe.lib.sanitizers import sanitize_text
from newspipe.models.right_mixin import RightMixin


class Bookmark(db.Model, RightMixin):  # type: ignore[name-defined]
    """
    Represent a bookmark.
    """

    id = db.Column(db.Integer(), primary_key=True)
    href = db.Column(db.String(), default="")
    title = db.Column(db.String(), default="")
    description = db.Column(db.String(), default="")
    shared = db.Column(db.Boolean(), default=False)
    to_read = db.Column(db.Boolean(), default=False)
    time = db.Column(db.DateTime(), default=datetime.utcnow)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))

    # relationships
    tags = db.relationship(
        "BookmarkTag",
        # back_populates="bookmark",
        cascade="all, delete-orphan",
        foreign_keys="[BookmarkTag.bookmark_id]",
    )
    tags_proxy = association_proxy("tags", "text")

    @validates("href")
    def validates_href(self, key, value):
        return str(value).strip()

    @validates("title")
    def validates_title(self, key, value):
        value = value.strip()
        assert 3 <= len(value) <= 50, AssertionError("Maximum length for title: 50")
        cleaned = sanitize_text(value)
        return cleaned

    @validates("description")
    def validates_description(self, key, value):
        value = value.strip()
        assert 3 <= len(value) <= 50, AssertionError(
            "Maximum length for description: 250"
        )
        cleaned = sanitize_text(value)
        return cleaned

    def __repr__(self):
        return "<Bookmark %r>" % (self.href)

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
__date__ = "$Date: 2026/06/28 $"
__revision__ = "$Date: 2026/06/28 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

from datetime import datetime

from sqlalchemy.orm import validates

from newspipe.bootstrap import db
from newspipe.lib.sanitizers import sanitize_text
from newspipe.models.right_mixin import RightMixin

# Maximum length (in characters) stored for a note's content.
MAX_NOTE_LENGTH = 5000


class ArticleNote(db.Model, RightMixin):
    "A note written by a user on an article."

    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.String(), default="")
    created_date = db.Column(db.DateTime(), default=datetime.utcnow)

    # foreign keys
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    article_id = db.Column(db.Integer(), db.ForeignKey("article.id"))

    # relationships
    article = db.relationship("Article", back_populates="notes")

    @validates("content")
    def validate_content(self, key, value):
        if value:
            # Final safety net: cap the length even if a caller skips the
            # length check performed in the web view.
            return sanitize_text(value)[:MAX_NOTE_LENGTH]
        return value

    def __repr__(self):
        return "<ArticleNote(id=%d, article_id=%s)>" % (self.id, self.article_id)

#! /usr/bin/env python
from sqlalchemy import Index
from sqlalchemy.orm import validates

from newspipe.bootstrap import db
from newspipe.lib.sanitizers import sanitize_text
from newspipe.models.right_mixin import RightMixin


class Category(db.Model, RightMixin):  # type: ignore[name-defined]
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())

    # relationships
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    feeds = db.relationship("Feed", cascade="all,delete-orphan")
    articles = db.relationship("Article", cascade="all,delete-orphan")

    # index
    idx_category_uid = Index("user_id")

    # api whitelists
    @staticmethod
    def _fields_base_read():
        return {"id", "user_id"}

    @staticmethod
    def _fields_base_write():
        return {"name"}

    @validates("name")
    def validates_name(self, key: str, value: str) -> str:
        assert 3 <= len(value) <= 20, AssertionError("Maximum length for name: 20")
        value = value.strip()
        cleaned = sanitize_text(value)
        return cleaned

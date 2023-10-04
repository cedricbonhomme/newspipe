#! /usr/bin/env python
from sqlalchemy import ForeignKeyConstraint, Index

from newspipe.bootstrap import db


class ArticleTag(db.Model):
    text = db.Column(db.String, primary_key=True, unique=False)

    # foreign keys
    article_id = db.Column(
        db.Integer, db.ForeignKey("article.id", ondelete="CASCADE"), primary_key=True
    )

    # relationships
    article = db.relationship(
        "Article", back_populates="tag_objs", foreign_keys=[article_id]
    )

    def __init__(self, text):
        self.text = text

    __table_args__ = (
        ForeignKeyConstraint([article_id], ["article.id"], ondelete="CASCADE"),
        Index("ix_articletag_aid", article_id),
    )


class BookmarkTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, unique=False)

    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    bookmark_id = db.Column(db.Integer, db.ForeignKey("bookmark.id"))

    # relationships
    bookmark = db.relationship(
        "Bookmark",
        back_populates="tags",
        cascade="all,delete",
        foreign_keys=[bookmark_id],
    )

    # def __init__(self, text, user_id):
    #     self.text = text
    #     self.user_id = user_id

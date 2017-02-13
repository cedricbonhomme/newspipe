#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bootstrap import db


class ArticleTag(db.Model):
    text = db.Column(db.String, primary_key=True, unique=False)

    # foreign keys
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'),
                        primary_key=True)

    # relationships
    article = db.relationship('Article', back_populates='tag_objs',
                           foreign_keys=[article_id])

    def __init__(self, text):
        self.text = text


class BookmarkTag(db.Model):
    text = db.Column(db.String, primary_key=True, unique=False)

    # foreign keys
    bookmark_id = db.Column(db.Integer, db.ForeignKey('bookmark.id', ondelete='CASCADE'),
                        primary_key=True)

    # relationships
    bookmark = db.relationship('Bookmark', back_populates='tag_objs',
                           foreign_keys=[bookmark_id])

    def __init__(self, text):
        self.text = text

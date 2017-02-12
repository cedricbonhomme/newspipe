#! /usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from bootstrap import db


class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    text = Column(String, unique=False)
    obj = db.Column(db.String, default='article')
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)

    __mapper_args__ = {
            'polymorphic_on': obj
        }


    def __init__(self, text):
        self.text = text


class ArticleTag(Tag):
    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }
    id = db.Column(db.Integer, db.ForeignKey('tag.id', ondelete='CASCADE'),
                    primary_key=True)

    # relationships
    article_id = Column(Integer, ForeignKey('article.id', ondelete='CASCADE'),
                        nullable=False)
    article = relationship('Article', back_populates='tag_objs',
                           foreign_keys=[article_id])


class BookmarkTag(Tag):
    __mapper_args__ = {
        'polymorphic_identity': 'bookmark'
    }
    id = db.Column(db.Integer, db.ForeignKey('tag.id', ondelete='CASCADE'),
                    primary_key=True)

    # relationships
    bookmark_id = Column(Integer, ForeignKey('bookmark.id', ondelete='CASCADE'),
                        nullable=False)
    bookmark = relationship('Bookmark', back_populates='tag_objs',
                           foreign_keys=[bookmark_id])

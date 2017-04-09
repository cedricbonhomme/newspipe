#! /usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from bootstrap import db


class Tag(db.Model):
    text = Column(String, primary_key=True, unique=False)

    # foreign keys
    article_id = Column(Integer, ForeignKey('article.id', ondelete='CASCADE'),
                        primary_key=True)

    # relationships
    article = relationship('Article', back_populates='tag_objs',
                           foreign_keys=[article_id])

    def __init__(self, text):
        self.text = text

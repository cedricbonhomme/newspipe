#! /usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *
from datetime import datetime

from werkzeug import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

import bson.objectid

class User(Document, UserMixin):
    firstname  = StringField(required=True)
    lastname = StringField(required = True)
    email = EmailField(required=True, unique=True)
    pwdhash = StringField(required=True)
    feeds = ListField(EmbeddedDocumentField('Feed'))
    created_at = DateTimeField(required=True, default=datetime.now)

    def get_id(self):
        return self.email

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    #required for administrative interface
    def __unicode__(self):
        return self.email

class Feed(EmbeddedDocument):
    oid = ObjectIdField(default=bson.objectid.ObjectId , primary_key=True)
    title = StringField(required=True)
    link = StringField(required=True)
    site_link = StringField(required=True)
    mail = BooleanField()
    articles = ListField(ReferenceField('Article', dbref = False))
    created_date = DateTimeField(required=True, default=datetime.now)

    meta = {
        'ordering': ['+title']
    }

    def __str__(self):
        return 'Feed: %s' % self.title

class Article(Document):
    date = DateTimeField(required=True)
    link = StringField(required=True)
    title = StringField(required=True)
    content = StringField(required=True)
    readed = BooleanField()
    like = BooleanField()
    retrieved_date = DateTimeField(required=True, default=datetime.now)

    meta = {
        'ordering': ['-date'],
        'indexes': [
            {'fields': ['-date'],
              'sparse': True, 'types': False },
        ]
    }

    def __str__(self):
        return 'Article: %s' % self.title

if __name__ == "__main__":
    # Point of entry in execution mode
    db = connect('pyaggr3g470r1')
    db.drop_database('pyaggr3g470r1')


    from werkzeug import generate_password_hash
    password = generate_password_hash("admin")
    user1 = User(firstname="Cédric", lastname="Bonhomme", \
                email="kimble.mandel@gmail.com", pwdhash=password)


    import mongodb
    mongo = mongodb.Articles("127.0.0.1", 27017, \
                        "pyaggr3g470r", "***", "")
    feeds = mongo.get_all_feeds()
    for feed in feeds:
        articles = []
        feed_articles = mongo.get_articles(feed["feed_id"])
        feed_articles = sorted(feed_articles, key=lambda t: t['article_date'], reverse=True)
        for article in feed_articles:
            article1 = Article(date=article["article_date"], link=article["article_link"], \
                       title=article["article_title"], content=article["article_content"], \
                        readed=article["article_readed"], like=article["article_like"], \
                        retrieved_date=article["article_date"])

            articles.append(article1)
            article1.save()

        sorted(articles, key=lambda t: t.date, reverse=True)

        feed1 = Feed(title=feed["feed_title"], link=feed["feed_link"],
                 site_link=feed["site_link"], mail=feed["mail"],
                 articles=articles)
        #feed1.save()
        user1.feeds.append(feed1)
        user1.save()
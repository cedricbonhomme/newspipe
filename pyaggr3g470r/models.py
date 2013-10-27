#! /usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *
from datetime import datetime

from werkzeug import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

class User(Document, UserMixin):
    firstname  = StringField(required=True)
    lastname = StringField(required = True)
    email = EmailField(required=True, unique=True)
    pwdhash = StringField(required=True)
    created_at = DateTimeField(required=True, default=datetime.now)

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    #required for administrative interface
    def __unicode__(self):
        return self.nickname

class Feed(Document):
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

    Feed.drop_collection()
    try:
        Article.drop_collection()
        # pas de méthode save() pour un objet EmbeddedDocument.
    except:
        pass

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
        feed1.save()
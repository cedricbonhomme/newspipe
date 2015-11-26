#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bootstrap import application, db, populate_g, conf
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

import web.models

Migrate(application, db)

manager = Manager(application)
manager.add_command('db', MigrateCommand)

@manager.command
def db_empty():
    "Will drop every datas stocked in db."
    with application.app_context():
        populate_g()
        jarr.models.db_empty(db)

@manager.command
def db_create():
    "Will create the database from conf parameters."
    with application.app_context():
        populate_g()
        jarr.models.db_create(db)

@manager.command
def fetch(limit=100, retreive_all=False):
    "Crawl the feeds with the client crawler."
    from web.lib.crawler import CrawlerScheduler
    scheduler = CrawlerScheduler(conf.API_LOGIN, conf.API_PASSWD)
    scheduler.run(limit=limit, retreive_all=retreive_all)
    scheduler.wait()

@manager.command
def fetch_asyncio(user_id, feed_id):
    "Crawl the feeds with asyncio."
    import asyncio

    with application.app_context():
        populate_g()
        from flask import g
        from web.models import User
        from web import crawler
        users, feed_id = [], None
        try:
            users = User.query.filter(User.id == int(user_id)).all()
        except:
            users = User.query.all()
        finally:
            if users == []:
                users = User.query.all()

        try:
            feed_id = int(feed_id)
        except:
            feed_id = None

        loop = asyncio.get_event_loop()
        for user in users:
            if user.activation_key == "":
                print("Fetching articles for " + user.nickname)
                g.user = user
                feed_getter = crawler.retrieve_feed(loop, g.user, feed_id)
        loop.close()

from scripts.probes import ArticleProbe, FeedProbe
manager.add_command('probe_articles', ArticleProbe())
manager.add_command('probe_feeds', FeedProbe())

if __name__ == '__main__':
    manager.run()

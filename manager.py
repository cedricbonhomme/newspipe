#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bootstrap import application, db, populate_g
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

Migrate(application, db)

manager = Manager(application)
manager.add_command('db', MigrateCommand)

@manager.command
def db_empty():
    "Will drop every datas stocked in db."
    with application.app_context():
        populate_g()
        import pyaggr3g470r.models
        pyaggr3g470r.models.db_empty(db)

@manager.command
def db_create():
    "Will create the database from conf parameters."
    with application.app_context():
        populate_g()
        import pyaggr3g470r.models
        pyaggr3g470r.models.db_create(db)

@manager.command
def fetch(user, password, limit=100, retreive_all=False):
    "Crawl the feeds with the client crawler."
    from pyaggr3g470r.lib.crawler import CrawlerScheduler
    scheduler = CrawlerScheduler(user, password)
    scheduler.run(limit=limit, retreive_all=retreive_all)
    scheduler.wait()

@manager.command
def fetch_asyncio(user_id, feed_id):
    "Crawl the feeds with asyncio."
    with application.app_context():
        populate_g()
        from pyaggr3g470r.models import User
        from pyaggr3g470r import crawler
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

    for user in users:
        if user.activation_key == "":
            print("Fetching articles for " + user.nickname)
            feed_getter = crawler.retrieve_feed(user, feed_id)

if __name__ == '__main__':
    manager.run()

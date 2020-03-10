#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from werkzeug.security import generate_password_hash

import newspipe.models
from newspipe.bootstrap import application, db
from newspipe.controllers import UserController

logger = logging.getLogger("manager")

Migrate(application, db)

manager = Manager(application)
manager.add_command("db", MigrateCommand)


@manager.command
def db_empty():
    "Will drop every datas stocked in db."
    with application.app_context():
        newspipe.models.db_empty(db)


@manager.command
def db_create():
    "Will create the database from conf parameters."
    admin = {
        "is_admin": True,
        "is_api": True,
        "is_active": True,
        "nickname": "admin",
        "pwdhash": generate_password_hash(os.environ.get("ADMIN_PASSWORD", "password")),
    }
    with application.app_context():
        db.create_all()
        UserController(ignore_context=True).create(**admin)


@manager.command
def create_admin(nickname, password):
    "Will create an admin user."
    admin = {
        "is_admin": True,
        "is_api": True,
        "is_active": True,
        "nickname": nickname,
        "pwdhash": generate_password_hash(password),
    }
    with application.app_context():
        UserController(ignore_context=True).create(**admin)


@manager.command
def fetch_asyncio(user_id=None, feed_id=None):
    "Crawl the feeds with asyncio."
    import asyncio

    with application.app_context():
        from newspipe.crawler import default_crawler

        filters = {}
        filters["is_active"] = True
        filters["automatic_crawling"] = True
        if None is not user_id:
            filters["id"] = user_id
        users = UserController().read(**filters).all()

        try:
            feed_id = int(feed_id)
        except:
            feed_id = None

        loop = asyncio.get_event_loop()
        queue = asyncio.Queue(maxsize=3, loop=loop)

        producer_coro = default_crawler.retrieve_feed(queue, users, feed_id)
        consumer_coro = default_crawler.insert_articles(queue, 1)

        logger.info("Starting crawler.")
        start = datetime.now()
        loop.run_until_complete(asyncio.gather(producer_coro, consumer_coro))
        end = datetime.now()
        loop.close()
        logger.info("Crawler finished in {} seconds.".format((end - start).seconds))


if __name__ == "__main__":
    manager.run()

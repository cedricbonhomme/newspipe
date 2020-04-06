#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime

import click
from werkzeug.security import generate_password_hash

import newspipe.models
from newspipe.bootstrap import application, db
from newspipe.controllers import UserController

logger = logging.getLogger("commands")


@application.cli.command("db_empty")
def db_empty():
    "Will drop every datas stocked in db."
    with application.app_context():
        newspipe.models.db_empty(db)


@application.cli.command("db_create")
def db_create():
    "Will create the database from conf parameters."
    with application.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(e)


@application.cli.command("create_admin")
@click.option('--nickname', default='admin', help='Nickname')
@click.option('--password', default='password', help='Password')
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


@application.cli.command("fetch_asyncio")
@click.option('--user-id', default=None, help='Id of the user')
@click.option('--feed-id', default=None, help='If of the feed')
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

#! /usr/bin/env python
import logging
from datetime import date
from datetime import datetime

import click
from dateutil.relativedelta import relativedelta
from werkzeug.security import generate_password_hash

import newspipe.models
from newspipe.bootstrap import application
from newspipe.bootstrap import db
from newspipe.controllers import ArticleController
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
@click.option("--nickname", default="admin", help="Nickname")
@click.option("--password", default="password", help="Password")
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
        try:
            UserController(ignore_context=True).create(**admin)
        except Exception as e:
            print(e)


@application.cli.command("delete_user")
@click.option("--user-id", required=True, help="Id of the user to delete.")
def delete_user(user_id=None):
    "Delete the user with the id specified in the command line."
    try:
        user = UserController().delete(user_id)
        print(f"User {user.nickname} deleted")
    except Exception as e:
        print(e)


@application.cli.command("delete_inactive_users")
@click.option("--last-seen", default=6, help="Number of months since last seen.")
def delete_inactive_users(last_seen):
    """Delete inactive users (inactivity is given in parameter and specified in number
    of months)."""
    filter = {}
    filter["last_seen__lt"] = date.today() - relativedelta(months=last_seen)
    users = UserController().read(**filter)
    for user in users:
        db.session.delete(user)
        try:
            print(f"Deleting user {user.nickname}...")
            db.session.commit()
        except Exception:
            db.session.rollback()
    print("Inactive users deleted.")


@application.cli.command("disable_inactive_users")
@click.option("--last-seen", default=6, help="Number of months since last seen.")
def disable_inactive_users(last_seen):
    """Disable inactive users (inactivity is given in parameter and specified in number
    of months)."""
    filter = {}
    filter["last_seen__lt"] = date.today() - relativedelta(months=last_seen)
    users = UserController().read(**filter)
    for user in users:
        user.is_active = False
        user.is_public_profile = False
        user.automatic_crawling = False
        try:
            print(f"Updating user {user.nickname}...")
            db.session.commit()
        except Exception:
            db.session.rollback()
    print("Inactive users disabled.")


@application.cli.command("delete_read_articles")
def delete_read_articles():
    "Delete read articles (and not liked) retrieved since more than 60 days ago."
    filter = {}
    filter["user_id__ne"] = 1
    filter["readed"] = True
    filter["like"] = False
    filter["retrieved_date__lt"] = date.today() - relativedelta(days=60)
    articles = ArticleController().read(**filter).limit(5000)
    for article in articles:
        try:
            db.session.delete(article)
            db.session.commit()
        except Exception:
            db.session.rollback()
    print("Read articles deleted.")


@application.cli.command("fix_article_entry_id")
def fix_article_entry_id():
    filter = {}
    filter["entry_id"] = None
    articles = ArticleController().read(**filter).limit(50)
    for article in articles:
        try:
            article.entry_id = str(article.id)
            db.session.commit()
        except Exception:
            db.session.rollback()


@application.cli.command("fetch_asyncio")
@click.option("--user-id", default=None, help="Id of the user")
@click.option("--feed-id", default=None, help="If of the feed")
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
        except Exception:
            feed_id = None

        loop = asyncio.get_event_loop()
        queue = asyncio.Queue(maxsize=3)

        producer_coro = default_crawler.retrieve_feed(queue, users, feed_id)
        consumer_coro = default_crawler.insert_articles(queue, 1)

        logger.info("Starting crawler.")
        start = datetime.now()
        loop.run_until_complete(asyncio.gather(producer_coro, consumer_coro))
        end = datetime.now()
        loop.close()
        logger.info(f"Crawler finished in {(end - start).seconds} seconds.")

#! /usr/bin/env python
# Newspipe - A web news aggregator.
# Copyright (C) 2010-20243 Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information: https://sr.ht/~cedric/newspipe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 4.2 $"
__date__ = "$Date: 2010/09/02 $"
__revision__ = "$Date: 2019/05/21 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "AGPLv3"

import asyncio
import io
import logging
from datetime import datetime, timedelta

import dateutil.parser
import feedparser

from newspipe.bootstrap import application
from newspipe.controllers import ArticleController, FeedController
from newspipe.lib.article_utils import construct_article, extract_id
from newspipe.lib.feed_utils import construct_feed_from, is_parsing_ok
from newspipe.lib.utils import newspipe_get

logger = logging.getLogger(__name__)

sem = asyncio.Semaphore(5)


async def parse_feed(user, feed):
    """
    Fetch a feed.
    Update the feed and return the articles.
    """
    parsed_feed = None
    up_feed = {}
    articles = []
    resp = None
    # with (await sem):
    try:
        logger.info(f"Retrieving feed {feed.link}")
        resp = newspipe_get(feed.link, timeout=5)
    except Exception:
        logger.info(f"Problem when reading feed {feed.link}")
        return

    if None is resp:
        return

    try:
        content = io.BytesIO(resp.content)
        parsed_feed = feedparser.parse(content)
    except Exception as e:
        up_feed["last_error"] = str(e)
        up_feed["error_count"] = feed.error_count + 1
        logger.exception("error when parsing feed: " + str(e))

    up_feed["last_retrieved"] = datetime.now(dateutil.tz.tzlocal())
    if parsed_feed is None:
        try:
            FeedController().update({"id": feed.id}, up_feed)
        except Exception as e:
            logger.exception("something bad here: " + str(e))
        return

    if not is_parsing_ok(parsed_feed):
        up_feed["last_error"] = str(parsed_feed["bozo_exception"])
        up_feed["error_count"] = feed.error_count + 1
        FeedController().update({"id": feed.id}, up_feed)
        return
    if parsed_feed["entries"] != []:
        articles = parsed_feed["entries"]

    up_feed["error_count"] = 0
    up_feed["last_error"] = ""

    # Feed information
    try:
        up_feed.update(construct_feed_from(feed.link, parsed_feed))
    except Exception:
        logger.exception(f"error when constructing feed: {feed.link}")
    if feed.title and "title" in up_feed:
        # do not override the title set by the user
        del up_feed["title"]
    try:
        FeedController().update({"id": feed.id}, up_feed)
    except Exception:
        logger.exception(f"error when updating feed: {feed.link}")

    return articles


async def insert_articles(queue, nḅ_producers=1):
    """Consumer coroutines."""
    nb_producers_done = 0
    while True:
        item = await queue.get()
        if item is None:
            nb_producers_done += 1
            if nb_producers_done == nḅ_producers:
                logger.info("All producers done.")
                logger.info("Process finished.")
                break
            continue

        user, feed, articles = item

        if None is articles:
            logger.info("None")
            articles = []

        logger.info(f"Inserting articles for {feed.link}")

        art_contr = ArticleController(user.id)
        for article in articles:
            new_article = await construct_article(article, feed)

            try:
                existing_article_req = art_contr.read(
                    user_id=user.id, feed_id=feed.id, entry_id=extract_id(article)
                )
            except Exception as e:
                logger.exception("existing_article_req: " + str(e))
                continue
            exist = existing_article_req.count() != 0
            if exist:
                continue

            # insertion of the new article
            try:
                art_contr.create(**new_article)
                logger.info("New article added: {}".format(new_article["link"]))
            except Exception:
                logger.exception("Error when inserting article in database.")
                continue


async def retrieve_feed(queue, users, feed_id=None):
    """
    Launch the processus.
    """
    for user in users:
        logger.info(f"Starting to retrieve feeds for {user.nickname}")
        filters = {}
        filters["user_id"] = user.id
        if feed_id is not None:
            filters["id"] = feed_id
        filters["enabled"] = True
        filters["error_count__lt"] = application.config["DEFAULT_MAX_ERROR"]
        filters["last_retrieved__lt"] = datetime.now() - timedelta(
            minutes=application.config["FEED_REFRESH_INTERVAL"]
        )
        # feeds = FeedController().read(**filters).all()
        feeds = []  # temporary fix for: sqlalchemy.exc.OperationalError:
        # (psycopg2.OperationalError) SSL SYSCALL error: EOF detected
        for feed in user.feeds:
            if not feed.enabled:
                continue
            if feed.error_count > application.config["DEFAULT_MAX_ERROR"]:
                continue
            if feed.last_retrieved > (
                datetime.now()
                - timedelta(minutes=application.config["FEED_REFRESH_INTERVAL"])
            ):
                continue
            if None is feed_id or (feed_id and feed_id == feed.id):
                feeds.append(feed)

        if feeds == []:
            logger.info(f"No feed to retrieve for {user.nickname}")

        for feed in feeds:
            articles = await parse_feed(user, feed)
            await queue.put((user, feed, articles))

    await queue.put(None)

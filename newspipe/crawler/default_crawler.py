#! /usr/bin/env python
# Newspipe - A web news aggregator.
# Copyright (C) 2010-2025 Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information: https://github.com/cedricbonhomme/newspipe
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
from datetime import datetime, timedelta, timezone

import aiohttp
import feedparser

from newspipe.bootstrap import application
from newspipe.controllers import ArticleController, FeedController
from newspipe.lib.article_utils import construct_article, extract_id
from newspipe.lib.feed_utils import construct_feed_from, is_parsing_ok

# from newspipe.lib.utils import newspipe_get

logger = logging.getLogger(__name__)

sem = asyncio.Semaphore(10)  # max concurrent requests

logger = logging.getLogger(__name__)


async def parse_feed(user, feed, session, timeout=10):
    """Fetch and parse a feed asynchronously; update DB, return list of articles."""
    async with sem:
        up_feed = {"last_retrieved": datetime.now(timezone.utc)}
        articles = []

        try:
            logger.info(f"Retrieving feed {feed.link}")
            async with session.get(feed.link, timeout=timeout) as resp:
                if resp.status != 200:
                    up_feed["last_error"] = f"HTTP {resp.status}"
                    up_feed["error_count"] = feed.error_count + 1
                    await asyncio.to_thread(
                        FeedController().update, {"id": feed.id}, up_feed
                    )
                    return []

                content = await resp.read()
                parsed_feed = feedparser.parse(io.BytesIO(content))

        except Exception as e:
            up_feed["last_error"] = str(e)
            up_feed["error_count"] = feed.error_count + 1
            logger.exception(f"Error fetching/parsing feed {feed.link}: {e}")
            await asyncio.to_thread(FeedController().update, {"id": feed.id}, up_feed)
            return []

        if not is_parsing_ok(parsed_feed):
            up_feed["last_error"] = str(
                parsed_feed.get("bozo_exception", "Unknown parse error")
            )
            up_feed["error_count"] = feed.error_count + 1
            await asyncio.to_thread(FeedController().update, {"id": feed.id}, up_feed)
            return []

        if parsed_feed.entries:
            articles = parsed_feed.entries

        up_feed["error_count"] = 0
        up_feed["last_error"] = ""

        try:
            up_feed.update(construct_feed_from(feed.link, parsed_feed))
            if feed.title and "title" in up_feed:
                del up_feed["title"]
        except Exception as meta_err:
            logger.exception(f"Error constructing feed metadata: {meta_err}")

        await asyncio.to_thread(FeedController().update, {"id": feed.id}, up_feed)
        return articles


async def parse_feed_with_user(user, feed, session):
    """Wrapper to include user and feed with articles for queue."""
    articles = await parse_feed(user, feed, session)
    return (user, feed, articles)


async def insert_articles(queue, nb_producers=1):
    """Consumer coroutine: read (user, feed, articles) from queue and insert in DB."""
    nb_producers_done = 0

    while True:
        item = await queue.get()
        if item is None:
            nb_producers_done += 1
            if nb_producers_done == nb_producers:
                logger.info("All producers done.")
                logger.info("Process finished.")
                break
            continue

        user, feed, articles = item
        if articles is None:
            articles = []

        logger.info(f"Inserting {len(articles)} articles for {feed.link}")

        art_contr = ArticleController(user.id)

        for article in articles:
            new_article = await construct_article(article, feed)

            try:
                # run blocking DB query in thread
                existing_article_req = await asyncio.to_thread(
                    art_contr.read,
                    user_id=user.id,
                    feed_id=feed.id,
                    entry_id=extract_id(article),
                )
            except Exception as e:
                logger.exception("Error checking for existing article: %s", e)
                continue

            exist = existing_article_req.count() != 0
            if exist:
                continue

            try:
                await asyncio.to_thread(art_contr.create, **new_article)
                logger.debug("New article added: %s", new_article["link"])
            except Exception as e:
                logger.exception("Error inserting article: %s", e)


async def retrieve_feed(queue, users, feed_id=None, num_workers=1):
    """Retrieve feeds for all users concurrently, push (user, feed, articles) to queue."""
    now = datetime.now(timezone.utc)

    async with aiohttp.ClientSession() as session:
        tasks = []

        for user in users:
            logger.info(f"Starting to retrieve feeds for {user.nickname}")

            feeds = []
            for feed in user.feeds:
                last = feed.last_retrieved
                if last is not None and last.tzinfo is None:
                    last = last.replace(tzinfo=timezone.utc)

                if (
                    feed.enabled
                    and feed.error_count <= application.config["DEFAULT_MAX_ERROR"]
                    and (
                        last is None
                        or last
                        <= now
                        - timedelta(minutes=application.config["FEED_REFRESH_INTERVAL"])
                    )
                    and (feed_id is None or feed_id == feed.id)
                ):
                    feeds.append(feed)

            if not feeds:
                logger.info(f"No feed to retrieve for {user.nickname}")
                continue

            for feed in feeds:
                tasks.append(
                    asyncio.create_task(parse_feed_with_user(user, feed, session))
                )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.exception(f"Error fetching feed: {result}")
                continue
            # always a tuple (user, feed, articles)
            await queue.put(result)

    # send termination signals for consumers
    for _ in range(num_workers):
        await queue.put(None)

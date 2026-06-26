#! /usr/bin/env python
# Newspipe - A web news aggregator.
# Copyright (C) 2010-2026 Cédric Bonhomme - https://www.cedricbonhomme.org
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
import os
from datetime import datetime, timedelta, timezone

import aiohttp
import feedparser

from newspipe.bootstrap import application
from newspipe.controllers import ArticleController, FeedController
from newspipe.lib.article_utils import construct_article, extract_id
from newspipe.lib.feed_utils import construct_feed_from, is_parsing_ok

# from newspipe.lib.utils import newspipe_get

# Ensure log directory exists
log_dir = os.path.join(os.path.dirname(__file__), "..", "var")
os.makedirs(log_dir, exist_ok=True)

crawler_log_path = os.path.join(log_dir, "crawler.log")

crawler_logger = logging.getLogger("newspipe.crawler")

# Add our file handler only if it's not already there
if not any(
    isinstance(h, logging.FileHandler)
    and os.path.abspath(getattr(h, "baseFilename", ""))
    == os.path.abspath(crawler_log_path)
    for h in crawler_logger.handlers
):
    handler = logging.FileHandler(crawler_log_path, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    crawler_logger.addHandler(handler)

crawler_logger.setLevel(logging.INFO)
# Prevent logs from bubbling up into the global newspipe.log
crawler_logger.propagate = False

# convenience alias for module-level logging
logger = crawler_logger


sem = asyncio.Semaphore(10)  # max concurrent requests

# Serialize blocking DB operations. The producer (feed updates) and the consumer
# (article inserts) run concurrently and both write through worker threads; with
# SQLite's single-writer model that races into "database is locked" errors, so
# DB access is funnelled through this lock. Backends that handle concurrent
# writes (e.g. PostgreSQL) skip the lock for better throughput (see _SERIALIZE_DB).
db_lock = asyncio.Lock()

_SERIALIZE_DB = application.config.get("SQLALCHEMY_DATABASE_URI", "").startswith(
    "sqlite"
)


async def run_db(func, *args, **kwargs):
    """Run a blocking DB call in a worker thread.

    On SQLite (single-writer) the call is serialized via ``db_lock`` to avoid
    "database is locked" errors; on other backends the lock is skipped.
    """
    if _SERIALIZE_DB:
        async with db_lock:
            return await asyncio.to_thread(func, *args, **kwargs)
    return await asyncio.to_thread(func, *args, **kwargs)


async def read_capped(resp, max_bytes):
    """Read a response body, raising ValueError if it exceeds ``max_bytes``.

    Guards against a malicious or misbehaving feed exhausting memory with an
    unbounded body. Checks the advertised Content-Length first, then enforces
    the limit while streaming in case the header is missing or lies.
    """
    if resp.content_length is not None and resp.content_length > max_bytes:
        raise ValueError(
            f"declared body size {resp.content_length} exceeds limit {max_bytes}"
        )
    chunks = []
    total = 0
    async for chunk in resp.content.iter_chunked(8192):
        total += len(chunk)
        if total > max_bytes:
            raise ValueError(f"body exceeds size limit {max_bytes}")
        chunks.append(chunk)
    return b"".join(chunks)


def register_feed_error(up_feed, feed, error_message):
    """Record a fetch error on ``up_feed`` and disable the feed if it has
    failed too many times in a row.

    Once ``error_count`` exceeds ``DEFAULT_MAX_ERROR`` the feed would no longer
    be fetched anyway (see ``retrieve_feed``); disabling it makes that explicit
    and surfaces the state in the UI so the user can fix or remove the feed.
    """
    error_count = feed.error_count + 1
    up_feed["last_error"] = error_message
    up_feed["error_count"] = error_count
    if error_count > application.config["DEFAULT_MAX_ERROR"]:
        up_feed["enabled"] = False
        up_feed["auto_disabled"] = True
        logger.warning(
            f"Disabling feed {feed.link} after {error_count} consecutive errors"
        )


def mark_feed_healthy(up_feed):
    """Clear the error state on ``up_feed`` after a successful fetch.

    Re-enables a feed that had been auto-disabled after too many errors but is
    now reachable again; a no-op in effect for already-enabled feeds.
    """
    up_feed["error_count"] = 0
    up_feed["last_error"] = ""
    up_feed["enabled"] = True
    up_feed["auto_disabled"] = False


async def parse_feed(feed, session, timeout=10):
    """Fetch and parse a feed asynchronously; update DB, return list of articles."""
    async with sem:
        up_feed = {"last_retrieved": datetime.now(timezone.utc)}
        articles = []

        # Send cached validators so unchanged feeds can answer 304 Not Modified
        # instead of re-sending the whole body.
        request_headers = {}
        if feed.etag:
            request_headers["If-None-Match"] = feed.etag
        if feed.last_modified:
            request_headers["If-Modified-Since"] = feed.last_modified

        try:
            logger.info(f"Retrieving feed {feed.link}")
            async with session.get(
                feed.link, timeout=timeout, headers=request_headers
            ) as resp:
                if resp.status == 304:
                    # Not modified since the last fetch: nothing new to parse.
                    logger.info(f"Feed not modified: {feed.link}")
                    mark_feed_healthy(up_feed)
                    await run_db(FeedController().update, {"id": feed.id}, up_feed)
                    return []

                if resp.status != 200:
                    logger.error(f"Error when retrieving feed {feed.link}")
                    register_feed_error(up_feed, feed, f"HTTP {resp.status}")
                    await run_db(FeedController().update, {"id": feed.id}, up_feed)
                    return []

                content = await read_capped(
                    resp,
                    application.config.get("CRAWLER_MAX_FEED_SIZE", 10 * 1024 * 1024),
                )
                # Persist the new validators only after the body is accepted, so
                # a rejected (oversized) response does not poison the cache.
                up_feed["etag"] = resp.headers.get("ETag", "")
                up_feed["last_modified"] = resp.headers.get("Last-Modified", "")
                parsed_feed = feedparser.parse(io.BytesIO(content))

        except Exception as e:
            register_feed_error(up_feed, feed, str(e))
            logger.exception(f"Error fetching/parsing feed {feed.link}: {e}")
            await run_db(FeedController().update, {"id": feed.id}, up_feed)
            return []

        if not is_parsing_ok(parsed_feed):
            register_feed_error(
                up_feed,
                feed,
                str(parsed_feed.get("bozo_exception", "Unknown parse error")),
            )
            await run_db(FeedController().update, {"id": feed.id}, up_feed)
            return []

        if parsed_feed.entries:
            articles = parsed_feed.entries

        mark_feed_healthy(up_feed)

        try:
            # construct_feed_from performs blocking (requests) HTTP calls to
            # fetch site metadata and the favicon; run it in a thread so it does
            # not stall the event loop and serialize the whole crawl.
            up_feed.update(
                await asyncio.to_thread(construct_feed_from, feed.link, parsed_feed)
            )
            if feed.title and "title" in up_feed:
                del up_feed["title"]
        except Exception as meta_err:
            logger.exception(f"Error constructing feed metadata: {meta_err}")

        await run_db(FeedController().update, {"id": feed.id}, up_feed)
        return articles


async def parse_feed_with_user(user, feed, session):
    """Wrapper to include user and feed with articles for queue."""
    articles = await parse_feed(
        feed, session, application.config.get("CRAWLER_TIMEOUT", 10)
    )
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

        # Resolve every entry id once and fetch the already-known ones in a
        # single query, instead of one lookup per article. construct_article is
        # deferred until after dedup so we never build (and possibly fetch) an
        # article that already exists.
        articles_by_id = [(article, extract_id(article)) for article in articles]
        entry_ids = [entry_id for _, entry_id in articles_by_id]

        existing_ids = set()
        if entry_ids:
            try:
                existing_ids = await run_db(
                    lambda: {
                        existing.entry_id
                        for existing in art_contr.read(
                            feed_id=feed.id, entry_id__in=entry_ids
                        ).all()
                    }
                )
            except Exception as e:
                logger.exception("Error checking for existing articles: %s", e)
                continue

        seen = set()
        for article, entry_id in articles_by_id:
            # Skip ids that already exist or are duplicated within this batch.
            if entry_id in existing_ids or entry_id in seen:
                continue
            seen.add(entry_id)

            new_article = await construct_article(article, feed)
            try:
                await run_db(art_contr.create, **new_article)
                logger.debug("New article added: %s", new_article["link"])
            except Exception as e:
                logger.exception("Error inserting article: %s", e)


async def retrieve_feed(queue, users, feed_id=None, num_workers=1):
    """Retrieve feeds for all users concurrently, push (user, feed, articles) to queue."""
    now = datetime.now(timezone.utc)

    headers = {
        "User-Agent": application.config.get(
            "CRAWLER_USER_AGENT",
            "Newspipe (https://github.com/cedricbonhomme/newspipe)",
        )
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []

        for user in users:
            logger.info(f"Starting to retrieve feeds for {user.nickname}")

            max_error = application.config["DEFAULT_MAX_ERROR"]
            retry_days = application.config.get("DISABLED_FEED_RETRY_INTERVAL", 7)

            feeds = []
            for feed in user.feeds:
                if feed_id is not None and feed_id != feed.id:
                    continue

                last = feed.last_retrieved
                if last is not None and last.tzinfo is None:
                    last = last.replace(tzinfo=timezone.utc)

                if feed.enabled and feed.error_count <= max_error:
                    # Active feed: refresh on the normal interval.
                    due = last is None or last <= now - timedelta(
                        minutes=application.config["FEED_REFRESH_INTERVAL"]
                    )
                elif not feed.enabled and feed.auto_disabled:
                    # Feed auto-disabled after too many errors: retry
                    # occasionally in case the source has recovered (e.g. a
                    # transient DNS failure or outage).
                    due = last is None or last <= now - timedelta(days=retry_days)
                else:
                    # Manually disabled feed: leave it alone.
                    due = False

                if due:
                    feeds.append(feed)

            if not feeds:
                logger.info(f"No feed to retrieve for {user.nickname}")
                continue

            for feed in feeds:
                tasks.append(
                    asyncio.create_task(parse_feed_with_user(user, feed, session))
                )

        # Enqueue each feed's result as soon as it finishes, rather than waiting
        # for every fetch to complete, so the consumer can insert articles while
        # the remaining feeds are still being retrieved.
        for completed in asyncio.as_completed(tasks):
            try:
                result = await completed
            except Exception as error:
                logger.exception(f"Error fetching feed: {error}")
                continue
            # always a tuple (user, feed, articles)
            await queue.put(result)

    # send termination signals for consumers
    for _ in range(num_workers):
        await queue.put(None)

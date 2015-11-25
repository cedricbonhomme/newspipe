#! /usr/bin/env python
# -*- coding: utf-8 -

# jarr - A Web based news aggregator.
# Copyright (C) 2010-2015  Cédric Bonhomme - https://www.JARR-aggregator.org
#
# For more information : https://github.com/JARR-aggregator/JARR/
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
__version__ = "$Revision: 3.2 $"
__date__ = "$Date: 2010/09/02 $"
__revision__ = "$Date: 2015/04/08 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "AGPLv3"

import asyncio
import logging
import feedparser
import dateutil.parser
from datetime import datetime
from sqlalchemy import or_

import conf
from bootstrap import db
from web.models import User
from web.controllers import FeedController, ArticleController
from web.lib.feed_utils import construct_feed_from
from web.lib.article_utils import construct_article, extract_id

logger = logging.getLogger(__name__)

sem = asyncio.Semaphore(5)

import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

@asyncio.coroutine
def get(*args, **kwargs):
    #kwargs["connector"] = aiohttp.TCPConnector(verify_ssl=False)
    try:
        #logger.info("Fetching the feed: " + args[0])
        #response = yield from aiohttp.request('GET', *args, **kwargs)
        #return (yield from response.read_and_close(decode=False))
        data = feedparser.parse(args[0])
        return data
    except Exception as e:
        raise e

@asyncio.coroutine
def parse_feed(user, feed):
    """
    Fetch a feed.
    """
    a_feed = None
    with (yield from sem):
        try:
            a_feed = yield from get(feed.link)
        except Exception as e:
            feed.last_error = str(e)
        finally:
            if a_feed is None:
                feed.error_count += 1
                db.session.commit()
                return

    up_feed = {}
    if a_feed['bozo'] == 1:
        up_feed['last_error'] = str(a_feed['bozo_exception'])
        up_feed['error_count'] = feed.error_count + 1
        db.session.commit()
    if a_feed['entries'] == []:
        return

    up_feed['last_retrieved'] = datetime.now(dateutil.tz.tzlocal())
    up_feed['error_count'] = 0
    up_feed['last_error'] = ""

    # Feed informations
    up_feed.update(construct_feed_from(feed.link, a_feed))
    if feed.title and 'title' in up_feed:
        del up_feed['title']
    FeedController().update({'id': feed.id}, up_feed)

    return a_feed['entries']


@asyncio.coroutine
def insert_database(user, feed):

    articles = yield from asyncio.async(parse_feed(user, feed))
    if None is articles:
        return []

    logger.debug('inserting articles for {}'.format(feed.title))

    logger.info("Database insertion...")
    new_articles = []
    art_contr = ArticleController(user.id)
    for article in articles:
        exist = art_contr.read(feed_id=feed.id,
                        **extract_id(article)).count() != 0
        if exist:
            logger.debug("Article %r (%r) already in the database.",
                         article.title, article.link)
            continue
        article = construct_article(article, feed)
        try:
            new_articles.append(art_contr.create(**article))
            logger.info("New article % (%r) added.",
                        article.title, article.link)
        except Exception as e:
            logger.exception("Error when inserting article in database:")
            continue
    return new_articles

@asyncio.coroutine
def init_process(user, feed):
    # Fetch the feed and insert new articles in the database
    articles = yield from asyncio.async(insert_database(user, feed))
    logger.debug('inserted articles for %s', feed.title)
    return articles

def retrieve_feed(loop, user, feed_id=None):
    """
    Launch the processus.
    """
    logger.info("Starting to retrieve feeds.")

    # Get the list of feeds to fetch
    user = User.query.filter(User.email == user.email).first()
    feeds = [feed for feed in user.feeds if
             feed.error_count <= conf.DEFAULT_MAX_ERROR and feed.enabled]
    if feed_id is not None:
        feeds = [feed for feed in feeds if feed.id == feed_id]

    if feeds == []:
        return
    # Launch the process for all the feeds
    tasks = []
    try:
        # Python 3.5 (test)
        tasks = [asyncio.ensure_future(init_process(user, feed))
                 for feed in feeds]
    except:
        tasks = [init_process(user, feed) for feed in feeds]
    try:
        loop.run_until_complete(asyncio.wait(tasks))
    except Exception:
        logger.exception('an error occured')

    logger.info("All articles retrieved. End of the processus.")

#! /usr/bin/env python
# -*- coding: utf-8 -

# newspipe - A Web based news aggregator.
# Copyright (C) 2010-2016  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : https://github.com/Newspipe/Newspipe
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
__version__ = "$Revision: 3.3 $"
__date__ = "$Date: 2010/09/02 $"
__revision__ = "$Date: 2015/12/07 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "AGPLv3"

import asyncio
import logging
import feedparser
import dateutil.parser
from datetime import datetime, timezone, timedelta
from sqlalchemy import or_

import conf
from bootstrap import db
from web.models import User
from web.controllers import FeedController, ArticleController
from lib.feed_utils import construct_feed_from, is_parsing_ok
from lib.article_utils import construct_article, extract_id, \
                                    get_article_content

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


async def get(*args, **kwargs):
    #kwargs["connector"] = aiohttp.TCPConnector(verify_ssl=False)
    try:
        data = feedparser.parse(args[0])
        return data
    except Exception as e:
        raise e


async def parse_feed(user, feed):
    """
    Fetch a feed.
    Update the feed and return the articles.
    """
    parsed_feed = None
    up_feed = {}
    articles = []
    with (await sem):
        try:
            parsed_feed = await get(feed.link)
        except Exception as e:
            up_feed['last_error'] = str(e)
            up_feed['error_count'] = feed.error_count + 1
            logger.exception("error when parsing feed: " + str(e))
        finally:
            up_feed['last_retrieved'] = datetime.now(dateutil.tz.tzlocal())
            if parsed_feed is None:
                try:
                    FeedController().update({'id': feed.id}, up_feed)
                except Exception as e:
                    logger.exception('something bad here: ' + str(e))
                return

    if not is_parsing_ok(parsed_feed):
        up_feed['last_error'] = str(parsed_feed['bozo_exception'])
        up_feed['error_count'] = feed.error_count + 1
        FeedController().update({'id': feed.id}, up_feed)
        return
    if parsed_feed['entries'] != []:
        articles = parsed_feed['entries']

    up_feed['error_count'] = 0
    up_feed['last_error'] = ""

    # Feed information
    construct_feed_from(feed.link, parsed_feed).update(up_feed)
    if feed.title and 'title' in up_feed:
        # do not override the title set by the user
        del up_feed['title']
    FeedController().update({'id': feed.id}, up_feed)

    return articles


async def insert_database(user, feed):
    articles = await parse_feed(user, feed)
    if None is articles:
        return []

    logger.info('Inserting articles for {}'.format(feed.title))

    new_articles = []
    art_contr = ArticleController(user.id)
    for article in articles:
        new_article = await construct_article(article, feed)

        try:
            existing_article_req = art_contr.read(feed_id=feed.id,
                            entry_id=extract_id(article))
        except Exception as e:
            logger.exception("existing_article_req: " + str(e))
            continue
        exist = existing_article_req.count() != 0
        if exist:
            continue
            # if the article has been already retrieved, we only update
            # the content or the title
            logger.info('Article already in the database: {}'. \
                            format(article['link']))
            existing_article = existing_article_req.first()

            if new_article['date'].replace(tzinfo=None) != \
                                                        existing_article.date:
                existing_article.date = new_article['date']
                existing_article.updated_date = new_article['date']
                if existing_article.title != new_article['title']:
                    existing_article.title = new_article['title']
                content = get_article_content(article)
                if existing_article.content != content:
                    existing_article.content = content
                    existing_article.readed = False
                art_contr.update({'entry_id': existing_article.entry_id},
                                                        existing_article.dump())
                logger.info('Article updated: {}'.format(article['link']))
            continue

        # insertion of the new article
        try:
            new_articles.append(art_contr.create(**new_article))
            logger.info('New article added: {}'.format(new_article['link']))
        except Exception:
            logger.exception('Error when inserting article in database:')
            continue
    return new_articles


async def init_process(user, feed):
    # Fetch the feed and insert new articles in the database
    try:
        articles = await insert_database(user, feed)
        logger.debug('inserted articles for %s', feed.title)
        return articles
    except Exception as e:
        logger.exception('init_process: ' + str(e))


def retrieve_feed(loop, user, feed_id=None):
    """
    Launch the processus.
    """
    logger.info('Starting to retrieve feeds for {}'.format(user.nickname))

    # Get the list of feeds to fetch
    filters = {}
    filters['user_id'] = user.id
    if feed_id is not None:
        filters['id'] = feed_id
    filters['enabled'] = True
    filters['error_count__lt'] = conf.DEFAULT_MAX_ERROR
    filters['last_retrieved__lt'] = datetime.now() - \
                                timedelta(minutes=conf.FEED_REFRESH_INTERVAL)
    feeds = FeedController().read(**filters).all()

    if feeds == []:
        logger.info('No feed to retrieve for {}'.format(user.nickname))
        return

    # Launch the process for all the feeds
    tasks = [asyncio.ensure_future(init_process(user, feed)) for feed in feeds]

    try:
        loop.run_until_complete(asyncio.wait(tasks))
    except Exception:
        logger.exception('an error occured')
    finally:
        logger.info('Articles retrieved for {}'.format(user.nickname))

#! /usr/bin/env python
# -*- coding: utf-8 -

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2015  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : https://bitbucket.org/cedricbonhomme/pyaggr3g470r/
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
import aiohttp
import logging
import requests
import feedparser
import dateutil.parser
from datetime import datetime
from bs4 import BeautifulSoup
from sqlalchemy import or_

from pyaggr3g470r import utils
import conf
from bootstrap import db
from pyaggr3g470r.models import User, Article

logger = logging.getLogger(__name__)

sem = asyncio.Semaphore(5)

@asyncio.coroutine
def get(*args, **kwargs):
    kwargs["connector"] = aiohttp.TCPConnector(verify_ssl=False)
    try:
        #logger.info("Fetching the feed: " + args[0])
        response = yield from aiohttp.request('GET', *args, **kwargs)
        return (yield from response.read_and_close(decode=False))
    except Exception as e:
        #print(e)
        raise e

@asyncio.coroutine
def parse_feed(user, feed):
    """
    Fetch a feed.
    """
    data = None

    with (yield from sem):
        try:
            data = yield from get(feed.link)
        except Exception as e:
            feed.last_error = str(e)
        finally:
            if data is None:
                feed.error_count += 1
                db.session.commit()
                return

    a_feed = feedparser.parse(data)
    if a_feed['bozo'] == 1:
        #logger.error(a_feed['bozo_exception'])
        feed.last_error = str(a_feed['bozo_exception'])
        feed.error_count += 1
        db.session.commit()
    if a_feed['entries'] == []:
        return

    feed.last_retrieved = datetime.now(dateutil.tz.tzlocal())
    feed.error_count = 0
    feed.last_error = ""

    # Feed informations
    if feed.title == "":
        try:
            feed.title = a_feed.feed.title
        except:
            feed.title = "No title"
    if feed.link == "":
        try:
            feed.link = a_feed.feed.link
        except:
            feed.link = ""
    if feed.description == "":
        try:
            feed.description = a_feed.feed.subtitle
        except:
            feed.description = ""
    db.session.commit()

    articles = []
    for article in a_feed['entries']:

        try:
            nice_url = article.link
        except:
            # if not able to get the link of the article, continue
            continue
        if conf.RESOLVE_ARTICLE_URL:
            try:
                # resolves URL behind proxies
                # (like feedproxy.google.com)
                r = requests.get(article.link, timeout=5.0)
                nice_url = r.url
            except Exception as error:
                logger.warning(
                        "Unable to get the real URL of %s. Error: %s",
                        article.link, error)
                pass
        # remove utm_* parameters
        nice_url = utils.clean_url(nice_url)

        try:
            entry_id = article.id
        except:
            entry_id = nice_url

        description = ""
        article_title = article.get('title', '')
        try:
            # article content
            description = article.content[0].value
        except AttributeError:
            # article description
            description = article.get('description', '')

        try:
            soup = BeautifulSoup(description, "lxml")

            # Prevents BeautifulSoup4 from adding extra <html><body> tags
            # to the soup with the lxml parser.
            if soup.html.body:
                description = soup.html.body.decode_contents()
            elif soup.html:
                description = soup.html.decode_contents()
            else:
                description = soup.decode()
        except:
            logger.error("Problem when sanitizing the content of the article %s (%s)",
                                article_title, nice_url)

        # Get the date of publication of the article
        post_date = None
        for date_key in ('published_parsed', 'published',
                        'updated_parsed', 'updated'):
            if not date_key in article:
                continue

            try:
                post_date = dateutil.parser.parse(article[date_key],
                        dayfirst=True)
                break
            except:
                try:  # trying to clean date field from letters
                    post_date = dateutil.parser.parse(
                                re.sub('[A-z]', '', article[date_key]),
                                dayfirst=True)
                    break
                except:
                    pass
        else:
            post_date = datetime.now(dateutil.tz.tzlocal())

        # create the models.Article object and append it to the list of articles
        article = Article(entry_id=entry_id, link=nice_url, title=article_title,
                        content=description, readed=False, like=False,
                        date=post_date, user_id=user.id,
                        feed_id=feed.id)
        articles.append(article)
    return articles

@asyncio.coroutine
def insert_database(user, feed):

    articles = yield from asyncio.async(parse_feed(user, feed))
    if None is articles:
        return []

    #print('inserting articles for {}'.format(feed.title))

    logger.info("Database insertion...")
    new_articles = []
    query1 = Article.query.filter(Article.user_id == user.id)
    query2 = query1.filter(Article.feed_id == feed.id)
    for article in articles:
        exist = query2.filter(or_(Article.entry_id==article.entry_id, Article.link==article.link)).count() != 0
        if exist:
            #logger.debug("Article %r (%r) already in the database.", article.title, article.link)
            continue
        new_articles.append(article)
        try:
            feed.articles.append(article)
            #db.session.merge(article)
            db.session.commit()
            #logger.info("New article % (%r) added.", article.title, article.link)
        except Exception as e:
            logger.error("Error when inserting article in database: " + str(e))
            continue
    #db.session.close()
    return new_articles

@asyncio.coroutine
def init_process(user, feed):
    # Fetch the feed and insert new articles in the database
    articles = yield from asyncio.async(insert_database(user, feed))
    #print('inserted articles for {}'.format(feed.title))
    return articles

def retrieve_feed(user, feed_id=None):
    """
    Launch the processus.
    """
    logger.info("Starting to retrieve feeds.")

    # Get the list of feeds to fetch
    user = User.query.filter(User.email == user.email).first()
    feeds = [feed for feed in user.feeds if
                feed.error_count <= conf.DEFAULT_MAX_ERROR and \
                feed.enabled]
    if feed_id is not None:
        feeds = [feed for feed in feeds if feed.id == feed_id]

    if feeds == []:
        return

    # Launch the process for all the feeds
    loop = asyncio.get_event_loop()
    tasks = []
    try:
        # Python 3.5 (test)
        tasks = [asyncio.ensure_future(init_process(user, feed)) for feed in feeds]
    except:
        tasks = [init_process(user, feed) for feed in feeds]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    logger.info("All articles retrieved. End of the processus.")

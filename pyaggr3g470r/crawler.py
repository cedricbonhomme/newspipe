#! /usr/bin/env python
# -*- coding: utf-8 -

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2014  Cédric Bonhomme - http://cedricbonhomme.org/
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
__version__ = "$Revision: 2.2 $"
__date__ = "$Date: 2010/09/02 $"
__revision__ = "$Date: 2014/07/13 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "AGPLv3"

import re
import socket
import logging
import feedparser
import urllib2
import requests
import dateutil.parser
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from requests.exceptions import *

import gevent.monkey
gevent.monkey.patch_all()
from gevent import Timeout
from gevent.pool import Pool

import utils
import conf
import emails
from pyaggr3g470r import db
from pyaggr3g470r.models import User, Article
if not conf.ON_HEROKU:
    import search as fastsearch


logger = logging.getLogger(__name__)

socket.setdefaulttimeout(5.0)

class TooLong(Exception):
    def __init__(self):
        """
        Log a when greenlet took to long to fetch a resource.
        """
        logger.warning("Greenlet took to long")


class FeedGetter(object):
    """
    This class is in charge of retrieving the feeds.
    """
    def __init__(self, email):
        """
        Initialization.
        """
        feedparser.USER_AGENT = conf.USER_AGENT
        if conf.HTTP_PROXY == "":
            self.proxy = urllib2.ProxyHandler({})
            self.proxies = {}
        else:
            self.proxy = urllib2.ProxyHandler({"http": conf.HTTP_PROXY,
                                               "https": conf.HTTP_PROXY})
            self.proxies = {
                            "http": "http://" + conf.HTTP_PROXY,
                            "https": "http://" + conf.HTTP_PROXY
                           }
        feedparser.USER_AGENT = conf.USER_AGENT
        self.user = User.query.filter(User.email == email).first()

    def retrieve_feed(self, feed_id=None):
        """
        Launch the processus.
        """
        logger.info("Starting to retrieve feeds.")

        # 1 - Get the list of feeds to fetch
        user = User.query.filter(User.email == self.user.email).first()
        feeds = [feed for feed in user.feeds if feed.enabled]
        if feed_id is not None:
            feeds = [feed for feed in feeds if feed.id == feed_id]

        # 2 - Fetch the feeds.
        # 'responses' contains all the jobs returned by
        # the function retrieve_async()
        responses = self.retrieve_async(feeds)
        elements = [item.value for item in responses if item.value is not None]

        # 3 - Insert articles in the database
        new_articles = self.insert_database(elements)

        # 4 - Indexation
        if not conf.ON_HEROKU:
            self.index(new_articles)

        # 5 - Mail notification
        if not conf.ON_HEROKU and conf.MAIL_ENABLED:
            self.mail_notification(new_articles)

        logger.info("All articles retrieved. End of the processus.")

    def retrieve_async(self, feeds):
        """
        Spawn different jobs in order to retrieve a list of feeds.
        Returns a list of jobs.
        """
        def fetch(feed):
            """
            Fetch a feed.
            """
            logger.info("Fetching the feed:" + feed.title)
            a_feed = feedparser.parse(feed.link, handlers=[self.proxy])
            if a_feed['entries'] == []:
                return

            # Feed informations
            if feed.title == "":
                try:
                    feed.title = a_feed.feed.title
                except:
                    feed.title = ""
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

            articles = []
            for article in a_feed['entries']:

                try:
                    nice_url = article.link.encode("utf-8")
                except:
                    # if not able to get the link of the article, continue
                    continue
                if conf.RESOLVE_ARTICLE_URL:
                    try:
                        # resolves URL behind proxies
                        # (like feedproxy.google.com)
                        r = requests.get(article.link, timeout=5.0,
                                            proxies=self.proxies)
                        nice_url = r.url.encode("utf-8")
                    except Timeout:
                        logger.warning(
                                "Timeout when getting the real URL of %s.",
                                article.link)
                        continue
                    except Exception as error:
                        logger.warning(
                                "Unable to get the real URL of %s. Error: %s",
                                article.link, error)
                        continue
                # remove utm_* parameters
                nice_url = utils.clean_url(nice_url)

                description = ""
                article_title = article.get('title', '')
                try:
                    # article content
                    description = article.content[0].value
                except AttributeError:
                    # article description
                    description = article.get('description', '')

                try:
                    description = BeautifulSoup(description, "lxml").decode()
                except:
                    logger.error("Problem when sanitizing the content of the article %s (%s)",
                                           article_title, nice_url)

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

                # create the models.Article object and append it to the list of articles
                article = Article(link=nice_url, title=article_title,
                                content=description, readed=False, like=False,
                                date=post_date, user_id=self.user.id,
                                feed_id=feed.id)
                articles.append(article)

            # return the feed with the list of retrieved articles
            return feed, articles

        pool = Pool(20)
        jobs = [pool.spawn(fetch, feed) for feed in feeds]
        pool.join()

        return jobs

    def insert_database(self, elements):
        """
        Insert articles in the database.
        """
        logger.info("Database insertion...")
        new_articles = []
        query1 = Article.query.filter(Article.user_id == self.user.id)
        for feed, articles in elements:
            query2 = query1.filter(Article.feed_id == feed.id)
            for article in articles:
                exist = query2.filter(Article.link == article.link).count() != 0
                if exist:
                    logger.debug("Article %r (%r) already in the database.",
                                 article.title, article.link)
                    continue
                if article.date is None:
                    article.date = datetime.now(dateutil.tz.tzlocal())

                new_articles.append(article)

                try:
                    feed.articles.append(article)
                    #db.session.merge(article)
                    db.session.commit()
                    logger.info("New article %r (%r) added.", article.title,
                                article.link)
                except Exception as e:
                    logger.error("Error when inserting article in database: " + str(e))
                    continue
        #db.session.close()
        return new_articles

    def index(self, new_articles):
        """
        Index new articles.
        """
        logger.info("Indexing new articles.")
        for element in new_articles:
            article = Article.query.filter(Article.user_id == self.user.id,
                                    Article.link == element.link).first()
            try:
                fastsearch.add_to_index(self.user.id, [article],
                                            article.source)
            except:
                logger.exception("Problem during indexation:")
        return True

    def mail_notification(self, new_articles):
        """
        Mail notification.
        """
        logger.info("Starting mail notification.")
        for element in new_articles:
            if element.source.email_notification:
                emails.new_article_notification(self.user, element.source, element)
        return True

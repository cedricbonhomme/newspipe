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
__version__ = "$Revision: 2.1 $"
__date__ = "$Date: 2010/09/02 $"
__revision__ = "$Date: 2014/04/13 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "AGPLv3"

import feedparser
import urllib2
import requests
from requests.exceptions import *
#from requests.packages.urllib3.exceptions import DecodeError
from urlparse import urlparse
from datetime import datetime

import gevent.monkey
#gevent.monkey.patch_socket()
gevent.monkey.patch_all()
from gevent import Timeout

from gevent.pool import Pool

"""
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.CRITICAL)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.CRITICAL)
requests_log.propagate = True
"""


import models
import conf
if not conf.ON_HEROKU:
    import search
import utils

if not conf.ON_HEROKU:
    from flask.ext.mail import Message
    from pyaggr3g470r import mail
    
from pyaggr3g470r import app, db
from pyaggr3g470r.models import User, Feed, Article

import log
pyaggr3g470r_log = log.Log("feedgetter")





HEADERS = {'User-Agent': conf.USER_AGENT}

class TooLong(Exception):
    def __init__(self):
        """
        Log a when greenlet took to long to fetch a resource.
        """
        pass #logger.warning("Greenlet took to long")


class FeedGetter(object):
    """
    This class is in charge of retrieving feeds listed in ./var/feed.lst.
    This class uses feedparser module from Mark Pilgrim.
    For each feed a new thread is launched.
    """
    def __init__(self, email):
        """
        Initializes the database connection.
        """
        feedparser.USER_AGENT = conf.USER_AGENT
        if conf.HTTP_PROXY == "":
            self.proxy = urllib2.ProxyHandler({})
            self.proxies = {}
        else:
            self.proxy = urllib2.ProxyHandler({"http" : conf.HTTP_PROXY, \
                                               "https": conf.HTTP_PROXY})
            self.proxies = {
                            "http": "http://" + conf.HTTP_PROXY,
                            "https": "http://" + conf.HTTP_PROXY
                           }
        feedparser.USER_AGENT = conf.USER_AGENT
        self.user = User.query.filter(User.email == email).first()

    def retrieve_async(self, feeds):
        """
        Spawn different jobs in order to retrieve a list of distant resources.
        Returns a list of models.Item objects.
        """
        def fetch(feed):
            """
            Fetch the content located at 'wsw_item.url'.
            """
            pyaggr3g470r_log.info("Fetching " + feed.title)
            a_feed = feedparser.parse(feed.link, handlers = [self.proxy])
            if a_feed['entries'] == []:
                return

            # Feed informations
            if feed.title == "":
                try:
                    feed.title = a_feed.feed.title
                except:
                    feed.title = ""
            if feed.description == "":
                try:
                    feed.description = a_feed.feed.subtitle
                except:
                    feed.description = ""

            articles = []
            for article in a_feed['entries']:

                nice_url = article.link.encode("utf-8")
                if conf.RESOLVE_ARTICLE_URL:
                    try:
                        # resolves URL behind proxies (like feedproxy.google.com)
                        r = requests.get(article.link, timeout=5.0, proxies=self.proxies)
                        nice_url = r.url.encode("utf-8")
                    except Timeout:
                        pyaggr3g470r_log.warning("Timeout when getting the real URL of %s." % (article.link,))
                        continue
                    except Exception as e:
                        pyaggr3g470r_log.warning("Unable to get the real URL of %s. Error: %s" % (article.link, str(e)))
                        continue
                # remove utm_* parameters
                nice_url = utils.clean_url(nice_url)

                description = ""
                article_title = ""
                try:
                    # article content
                    description = article.content[0].value
                except AttributeError:
                    try:
                        # article description
                        description = article.description
                    except Exception:
                        description = ""
                try:
                    description = BeautifulSoup(description, "html.parser").decode()
                    article_title = BeautifulSoup(article.title, "html.parser").decode()
                except Exception as E:
                    #pyaggr3g470r_log.error("Problem when sanitizing the content of the article %s (%s)" % (article_title, nice_url))
                    article_title = article.title

                try:
                    post_date = datetime(*article.published_parsed[:6])
                except:
                    post_date = datetime(*article.updated_parsed[:6])

                # save the article
                article = Article(link=nice_url, title=article_title, \
                                content=description, readed=False, like=False, date=post_date, \
                                user_id=self.user.id, feed_id=feed.id)
                articles.append(article)



            return feed, articles

        jobs = []
        pool = Pool(20)
        jobs = [pool.spawn(fetch, feed) for feed in feeds]
        pool.join()

        return jobs

    def insert_database(self, elements):
        """
        Insert articles in the database.
        """
        pyaggr3g470r_log.info("Database insertion...")
        for feed, articles in elements:

            for article in articles:

                exist = Article.query.filter(Article.user_id == self.user.id, Article.feed_id == feed.id, Article.link == article.link).first()
                if exist != None:
                    pyaggr3g470r_log.error("Article %s (%s) already in the database." % (article.title, article.link))
                    continue

                try:
                    feed.articles.append(article)
                    #db.session.merge(article)
                    db.session.commit()
                    pyaggr3g470r_log.info("New article %s (%s) added." % (article.title, article.link))
                except IntegrityError:
                    pyaggr3g470r_log.error("Article %s (%s) already in the database." % (article.title, article.link))
                    db.session.rollback()
                    continue
                except Exception as e:
                    pyaggr3g470r_log.error("Error when inserting article in database: " + str(e))
                    continue
        db.session.close()
        return True


    def retrieve_feed(self, feed_id=None):
        """
        Launch
        """
        user = User.query.filter(User.email == self.user.email).first()
        feeds = [feed for feed in user.feeds if feed.enabled]
        if feed_id != None:
            feeds = [feed for feed in feeds if feed.id == feed_id]

        responses = self.retrieve_async(feeds)

        self.insert_database([item.value for item in responses if item.value is not None])        
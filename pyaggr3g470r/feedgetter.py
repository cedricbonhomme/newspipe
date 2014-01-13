#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2013  Cédric Bonhomme - http://cedricbonhomme.org/
#
# For more information : http://bitbucket.org/cedricbonhomme/pyaggr3g470r/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 2.0 $"
__date__ = "$Date: 2010/09/02 $"
__revision__ = "$Date: 2013/11/10 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

import urllib2
import requests
import threading
import feedparser
from datetime import datetime
from urllib import urlencode
from urlparse import urlparse, parse_qs, urlunparse
from BeautifulSoup import BeautifulSoup
from mongoengine.queryset import NotUniqueError
from requests.exceptions import Timeout


import models
import conf
import search
import utils

from flask.ext.mail import Message
from pyaggr3g470r import app, mail

import log
pyaggr3g470r_log = log.Log("feedgetter")

list_of_threads = []

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
        self.user = models.User.objects(email=email).first()

    def retrieve_feed(self, feed_id=None):
        """
        Parse the file 'feeds.lst' and launch a thread for each RSS feed.
        """
        feeds = [feed for feed in self.user.feeds if feed.enabled]
        if feed_id != None:
            feeds = [feed for feed in feeds if str(feed.oid) == feed_id]
        for current_feed in feeds:
            try:
                # launch a new thread for the RSS feed
                thread = threading.Thread(None, self.process, \
                                           None, (current_feed, ))
                thread.start()
                list_of_threads.append(thread)
            except:
                pass

        # wait for all threads are done
        for th in list_of_threads:
            th.join()

    def process(self, feed):
        """
        Retrieves articles form the feed and add them to the database.
        """
        a_feed = feedparser.parse(feed.link, handlers = [self.proxy])
        if a_feed['entries'] == []:
            return

        articles = []
        for article in a_feed['entries']:

            nice_url = article.link.encode("utf-8")
            try:
                # resolves URL behind proxies (like feedproxy.google.com)
                r = requests.get(article.link, timeout=2.0, proxies=self.proxies)
                nice_url = r.url.encode("utf-8")
            except Timeout:
                pyaggr3g470r_log.warning("Timeout when getting the real URL of %s." % (article.link,))
            except Exception as e:
                pyaggr3g470r_log.warning("Unable to get the real URL of %s. Error: %s" % (article.link, str(e)))
            # remove utm_* parameters
            parsed_url = urlparse(nice_url)
            qd = parse_qs(parsed_url.query, keep_blank_values=True)
            filtered = dict((k, v) for k, v in qd.iteritems() if not k.startswith('utm_'))
            nice_url = urlunparse([
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                urlencode(filtered, doseq=True),
                parsed_url.fragment
            ])

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
            article = models.Article(post_date, nice_url, article_title, description, False, False)
            try:
                article.save()
                pyaggr3g470r_log.info("New article %s (%s) added." % (article_title, nice_url))
            except NotUniqueError:
                pyaggr3g470r_log.error("Article %s (%s) already in the database." % (article_title, nice_url))
                continue
            except Exception as e:
                pyaggr3g470r_log.error("Error when inserting article in database: " + str(e))
                continue
            articles.append(article)

            # add the article to the Whoosh index
            try:
                search.add_to_index([article], feed)
            except Exception as e:
                pyaggr3g470r_log.error("Whoosh error.")
                pass

            # email notification
            if conf.MAIL_ENABLED and feed.email_notification:
                with app.app_context():
                    msg = Message('[pyAggr3g470r] ' + feed.title + ' : ' + article.title, \
                                sender = conf.MAIL_FROM, recipients = [conf.MAIL_TO])
                    msg.body = utils.clear_string(description)
                    msg.html = description
                    mail.send(msg)

        # add the articles to the list of articles for the current feed
        feed.articles.extend(articles)
        feed.articles = sorted(feed.articles, key=lambda t: t.date, reverse=True)
        self.user.save()


if __name__ == "__main__":
    # Point of entry in execution mode
    feed_getter = FeedGetter()
    # Retrieve all feeds
    feed_getter.retrieve_feed()

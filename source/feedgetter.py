#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2012  Cédric Bonhomme - http://cedricbonhomme.org/
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
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2010/09/02 $"
__revision__ = "$Date: 2012/04/22 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

import hashlib
import threading
import feedparser
from BeautifulSoup import BeautifulSoup

from datetime import datetime

import conf
import utils
import mongodb

list_of_threads = []

class FeedGetter(object):
    """
    This class is in charge of retrieving feeds listed in ./var/feed.lst.
    This class uses feedparser module from Mark Pilgrim.
    For each feed a new thread is launched.
    """
    def __init__(self):
        """
        Initializes the base and variables.
        """
        # MongoDB connections
        self.articles = mongodb.Articles(conf.MONGODB_ADDRESS, conf.MONGODB_PORT)

    def retrieve_feed(self):
        """
        Parse the file 'feeds.lst' and launch a thread for each RSS feed.
        """
        with open("./var/feed.lst") as f:
            for a_feed in f:
                # test if the URL is well formed
                for url_regexp in utils.url_finders:
                    if url_regexp.match(a_feed):
                        the_good_url = url_regexp.match(a_feed).group(0).replace("\n", "")
                        try:
                            # launch a new thread for the RSS feed
                            thread = threading.Thread(None, self.process, \
                                                None, (the_good_url,))
                            thread.start()
                            list_of_threads.append(thread)
                        except:
                            pass
                        break

        # wait for all threads are done
        for th in list_of_threads:
            th.join()

    def process(self, the_good_url):
        """Request the URL

        Executed in a thread.
        """
        if utils.detect_url_errors([the_good_url]) == []:
            # if ressource is available add the articles in the base.
            self.add_into_database(the_good_url)

    def add_into_database(self, feed_link):
        """
        Add the articles of the feed 'a_feed' in the SQLite base.
        """
        a_feed = feedparser.parse(feed_link)
        if a_feed['entries'] == []:
            return
        try:
            feed_image = a_feed.feed.image.href
        except:
            feed_image = "/img/feed-icon-28x28.png"

        sha1_hash = hashlib.sha1()
        sha1_hash.update(feed_link.encode('utf-8'))
        feed_id = sha1_hash.hexdigest()

        collection_dic = {"feed_id": feed_id, \
                            "type": 0, \
                            "feed_image": feed_image, \
                            "feed_title": utils.clear_string(a_feed.feed.title.encode('utf-8')), \
                            "feed_link": feed_link, \
                            "site_link": a_feed.feed.link.encode('utf-8'), \
                            "mail": False \
                        }

        self.articles.add_collection(collection_dic)

        articles = []
        for article in a_feed['entries']:
            description = ""
            try:
                # article content
                description = article.content[0].value
            except AttributeError:
                try:
                    # article description
                    description = article.description
                except Exception:
                    description = ""
            description = str(BeautifulSoup(description))
            article_title = str(BeautifulSoup(article.title))

            try:
                post_date = datetime(*article.updated_parsed[:6])
            except:
                post_date = datetime(*article.published_parsed[:6])

            sha1_hash = hashlib.sha1()
            sha1_hash.update(article.link.encode('utf-8'))
            article_id = sha1_hash.hexdigest()

            article = {"article_id": article_id, \
                    "type":1, \
                    "article_date": post_date, \
                    "article_link": article.link.encode('utf-8'), \
                    "article_title": article_title, \
                    "article_content": description, \
                    "article_readed": False, \
                    "article_like": False \
                    }

            articles.append(article)

        self.articles.add_articles(articles, feed_id)

        # send new articles by e-mail if desired.
        #threading.Thread(None, utils.send_mail, None, (conf.mail_from, conf.mail_to, \
                            #a_feed.feed.title.encode('utf-8'), \
                            #article_title, description) \
                        #).start()


if __name__ == "__main__":
    # Point of entry in execution mode
    feed_getter = FeedGetter()
    feed_getter.retrieve_feed()

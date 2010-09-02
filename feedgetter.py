#! /usr/local/bin/python
#-*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.9 $"
__date__ = "$Date: 2010/04/15 $"
__copyright__ = "Copyright (c) 2010 Cedric Bonhomme"
__license__ = "GPLv3"

import re
import sqlite3
import threading
import feedparser

from datetime import datetime

import utils

feeds_list = []
list_of_threads = []


class FeedGetter(object):
    """
    """
    def __init__(self):
        """
        Initializes the base and variables.
        """
        # Create the base if not exists.
        utils.create_base()

        # mutex to protect the SQLite base
        self.locker = threading.Lock()

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
        SQLite objects created in a thread can only be used in that same thread !
        """
        # Protect this part of code.
        self.locker.acquire()

        self.conn = sqlite3.connect(utils.sqlite_base, isolation_level = None)
        self.c = self.conn.cursor()

        # Add the articles in the base.
        self.add_into_sqlite(the_good_url)

        self.conn.commit()
        self.c.close()

        # Release this part of code.
        self.locker.release()

    def add_into_sqlite(self, feed_link):
        """
        Add the articles of the feed 'a_feed' in the SQLite base.
        """
        a_feed = feedparser.parse(feed_link)
        if a_feed['entries'] == []:
            return
        try:
            feed_image = a_feed.feed.image.href
        except:
            feed_image = "/css/img/feed-icon-28x28.png"
        try:
            self.c.execute('insert into feeds values (?,?,?,?,?)', (\
                        utils.clear_string(a_feed.feed.title.encode('utf-8')), \
                        a_feed.feed.link.encode('utf-8'), \
                        feed_link, \
                        feed_image,
                        "0"))
        except sqlite3.IntegrityError:
                # feed already in the base
                pass
        for article in a_feed['entries']:
            description = ""
            try:
                description = article.content[0].value.encode('utf-8')
            except AttributeError:
                try:
                    description = article.description.encode('utf-8')
                except Exception, e:
                    description = ""

            try:
                self.c.execute('insert into articles values (?,?,?,?,?,?,?)', (\
                        datetime(*article.updated_parsed[:6]), \
                        utils.clear_string(article.title.encode('utf-8')), \
                        article.link.encode('utf-8'), \
                        description, \
                        "0", \
                        feed_link, \
                        "0"))
                result = self.c.execute("SELECT mail from feeds WHERE feed_site_link='" + \
                                a_feed.feed.link.encode('utf-8') + "'").fetchall()
                if result[0][0] == "1":
                    # send the article by e-mail
                    threading.Thread(None, utils.send_mail, \
                                        None, (utils.mail_from, utils.mail_to, \
                                        a_feed.feed.title.encode('utf-8'), description) \
                                    ).start()
            except sqlite3.IntegrityError:
                # article already in the base
                pass
            except:
                # Missing information (updated_parsed, ...)
                pass


if __name__ == "__main__":
    # Point of entry in execution mode
    feed_getter = FeedGetter()
    feed_getter.retrieve_feed()
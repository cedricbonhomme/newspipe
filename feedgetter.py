#! /usr/local/bin/python
#-*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.4 $"
__date__ = "$Date: 2010/02/01 $"
__copyright__ = "Copyright (c) 2010 Cedric Bonhomme"
__license__ = "GPLv3"

import re
import sqlite3
import hashlib
import threading
import feedparser

from datetime import datetime

url_finders = [ \
    re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?/[-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]*[^]'\\.}>\\),\\\"]"), \
    re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?"), \
    re.compile("(~/|/|\\./)([-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]|\\\\)+"), \
    re.compile("'\\<((mailto:)|)[-A-Za-z0-9\\.]+@[-A-Za-z0-9\\.]+"), \
]

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
        self.conn = sqlite3.connect("./var/feed.db", isolation_level = None)
        self.c = self.conn.cursor()
        self.c.execute('''create table if not exists rss_feed
                    (article_date text, article_title text, \
                    article_link text PRIMARY KEY, article_description text, \
                    feed_title text, feed_site_link text)''')
        self.conn.commit()
        self.c.close()

        # mutex to protect the SQLite base
        self.locker = threading.Lock()

    def retrieve_feed(self):
        """
        Parse the file 'feeds.lst' and launch a thread for each RSS feed.
        """
        for a_feed in feeds_file.readlines():
            # test if the URL is well formed
            for url_regexp in url_finders:
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

        self.conn = sqlite3.connect("./var/feed.db", isolation_level = None)
        self.c = self.conn.cursor()

        # Add the articles in the base.
        self.add_into_sqlite(feedparser.parse(the_good_url))

        self.conn.commit()
        self.c.close()

        # Release this part of code.
        self.locker.release()

    def add_into_sqlite(self, a_feed):
        """
        Add the articles of the feed 'a_feed' in the SQLite base.
        """
        for article in a_feed['entries']:
            try:
                description = article.description.encode('utf-8')
            except Exception, e:
                description = ""

            sha256_hash = hashlib.sha256()
            sha256_hash.update(article.link.encode('utf-8'))
            article_id = sha256_hash.hexdigest()

            try:
                self.c.execute('insert into rss_feed values (?,?,?,?,?,?)', (\
                        datetime(*article.updated_parsed[:6]), \
                        article.title.encode('utf-8'), \
                        article.link.encode('utf-8'), \
                        description, \
                        a_feed.feed.title.encode('utf-8'), \
                        a_feed.feed.link.encode('utf-8')))
            except sqlite3.IntegrityError:
                pass


if __name__ == "__main__":
    # Point of entry in execution mode
    try:
        feeds_file = open("./var/feed.lst")
    except:
        print "./feed.lst not found"
        exit(0)

    feed_getter = FeedGetter()
    feed_getter.retrieve_feed()
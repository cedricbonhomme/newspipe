#! /usr/local/bin/python
#-*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2010/29/01 $"
__copyright__ = "Copyright (c) 2010 Cedric Bonhomme"
__license__ = "GPLv3"

import re
import sqlite3
import threading
import feedparser

url_finders = [ \
    re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?/[-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]*[^]'\\.}>\\),\\\"]"), \
    re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?"), \
    re.compile("(~/|/|\\./)([-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]|\\\\)+"), \
    re.compile("'\\<((mailto:)|)[-A-Za-z0-9\\.]+@[-A-Za-z0-9\\.]+"), \
]

feeds_list = []
list_of_threads = []




def process(the_good_url):
    """Request the URL

    Executed in a thread.
    """
    feeds_list.append(feedparser.parse(the_good_url))

def retrieve_feed():
    """
    Parse the file 'feeds.lst' and launch a thread for each RSS feed.
    """
    conn = sqlite3.connect("feed.db", isolation_level = None)
    c = conn.cursor()
    c.execute('''create table rss_feed
                (date text, feed_title text, feed_site_link text, article_title text , article_link text)''')

    for a_feed in feeds_file.readlines():
        # test if the URL is well formed
        for url_regexp in url_finders:
            if url_regexp.match(a_feed):
                the_good_url = url_regexp.match(a_feed).group(0).replace("\n", "")
                try:
                    # launch a new thread for the RSS feed
                    thread = threading.Thread(None, process, \
                                        None, (the_good_url,))
                    thread.start()
                    list_of_threads.append(thread)
                except:
                    pass
                break

    # wait for all threads are done
    for th in list_of_threads:
        th.join()

    # when all jobs are done, insert articles in the base
    for a_feed in feeds_list:
        for article in a_feed['entries']:
            c.execute('insert into rss_feed values (?,?,?,?,?)', (\
                    "-".join([str(i) for i in list(article.updated_parsed)]), \
                    a_feed.feed.title.encode('utf-8'), \
                    a_feed.feed.link.encode('utf-8'), \
                    article.title.encode('utf-8'), \
                    article.link.encode('utf-8')))

    conn.commit()
    c.close()


if __name__ == "__main__":
    # Point of entry in execution mode
    try:
        feeds_file = open("./var/feed.lst")
    except:
        print "./feed.lst not found"
        exit(0)

    retrieve_feed()
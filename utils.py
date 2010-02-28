#! /usr/local/bin/python
#-*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2010/02/24 $"
__copyright__ = "Copyright (c) 2010 Cedric Bonhomme"
__license__ = "GPLv3"

import re
import pylab
import sqlite3
import hashlib

from datetime import datetime
from string import punctuation
from collections import defaultdict


def remove_html_tags(data):
    """
    Remove HTML tags for the search.
    """
    p = re.compile(r'<[^<]*?/?>')
    return p.sub('', data)

def top_words(dic_articles, n=10):
    """
    Return the n most frequent words in a list.
    """
    words = {}
    articles_content = ""
    for rss_feed_id in dic_articles.keys():
        for article in dic_articles[rss_feed_id]:
            articles_content += remove_html_tags(article[4].encode('utf-8'))
    words_gen = (word.strip(punctuation).lower() \
                        for word in articles_content.split() \
                                if len(word) >= 5)
    words = defaultdict(int)
    for word in words_gen:
        words[word] += 1
    top_words = sorted(words.iteritems(),
                key=lambda(word, count): (-count, word))[:n]
    return top_words

def create_histogram(words, file_name="./var/histogram.png"):
    """
    Create a histogram.
    """
    length = 10
    ind = pylab.arange(length) # abscissa
    width = 0.35 # bars width

    w = [elem[0] for elem in words]
    count = [int(elem[1]) for elem in words]

    max_count = max(count)  # maximal weight

    p = pylab.bar(ind, count, width, color='r')

    pylab.ylabel("Count")
    pylab.title("Most frequent words")
    pylab.xticks(ind + (width / 2), range(1, len(w)+1))
    pylab.xlim(-width, len(ind))

    # changing the ordinate scale according to the max.
    if max_count <= 100:
        pylab.ylim(0, max_count + 5)
        pylab.yticks(pylab.arange(0, max_count + 5, 5))
    elif max_count <= 200:
        pylab.ylim(0, max_count + 10)
        pylab.yticks(pylab.arange(0, max_count + 10, 10))
    elif max_count <= 600:
        pylab.ylim(0, max_count + 25)
        pylab.yticks(pylab.arange(0, max_count + 25, 25))
    elif max_count <= 800:
        pylab.ylim(0, max_count + 50)
        pylab.yticks(pylab.arange(0, max_count + 50, 50))

    pylab.savefig(file_name, dpi = 80)
    pylab.close()

def compare(stringtime1, stringtime2):
    """
    Compare two dates in the format 'yyyy-mm-dd hh:mm:ss'.
    """
    date1, time1 = stringtime1.split(' ')
    date2, time2 = stringtime2.split(' ')

    year1, month1, day1 = date1.split('-')
    year2, month2, day2 = date2.split('-')

    hour1, minute1, second1 = time1.split(':')
    hour2, minute2, second2 = time2.split(':')

    datetime1 = datetime(year=int(year1), month=int(month1), day=int(day1), \
                        hour=int(hour1), minute=int(minute1), second=int(second1))

    datetime2 = datetime(year=int(year2), month=int(month2), day=int(day2), \
                        hour=int(hour2), minute=int(minute2), second=int(second2))

    if datetime1 < datetime2:
        return -1
    elif datetime1 > datetime2:
        return 1
    return 0

def load_feed():
    """
    Load feeds and articles in a dictionary.
    """
    list_of_feeds = None
    list_of_articles = None
    try:
        conn = sqlite3.connect("./var/feed.db", isolation_level = None)
        c = conn.cursor()
        list_of_feeds = c.execute("SELECT * FROM feeds").fetchall()
    except:
        pass

    # articles[feed_id] = (article_id, article_date, article_title,
    #               article_link, article_description, article_readed)
    # feeds[feed_id] = (nb_article, nb_article_unreaded, feed_image,
    #               feed_title, feed_link, feed_site_link)
    articles, feeds = {}, {}
    if list_of_feeds is not None:
        for feed in list_of_feeds:
            list_of_articles = c.execute(\
                    "SELECT * FROM articles WHERE feed_link='" + \
                    feed[2] + "'").fetchall()

            if list_of_articles is not None:
                for article in list_of_articles:
                    sha256_hash = hashlib.sha256()
                    sha256_hash.update(article[5].encode('utf-8'))
                    feed_id = sha256_hash.hexdigest()
                    sha256_hash.update(article[2].encode('utf-8'))
                    article_id = sha256_hash.hexdigest()

                    article_list = [article_id, article[0], article[1], \
                        article[2], article[3], article[4]]

                    if feed_id not in articles:
                        articles[feed_id] = [article_list]
                    else:
                        articles[feed_id].append(article_list)


                # sort articles by date for each feeds
                for rss_feed_id in articles.keys():
                    articles[rss_feed_id].sort(lambda x,y: compare(y[1], x[1]))

                feeds[feed_id] = (len(articles[feed_id]), \
                                len([article for article in articles[feed_id] \
                                    if article[5]=="0"]), \
                                feed[3], feed[0], feed[2], feed[1] \
                                )
        c.close()

        return (articles, feeds)
    return (articles, feeds)
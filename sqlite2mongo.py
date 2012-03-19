#! /usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

import sqlite3
import mongodb

SQLITE_BASE = "./var/feed.db"


def load_feed():
    """
    Load feeds and articles in a dictionary.
    """
    mongo = mongodb.Articles()
    list_of_feeds = []
    list_of_articles = []

    try:
        conn = sqlite3.connect(SQLITE_BASE, isolation_level = None)
        c = conn.cursor()
        list_of_feeds = c.execute("SELECT * FROM feeds").fetchall()
    except:
        pass


    if list_of_feeds != []:
        # Walk through the list of feeds
        for feed in list_of_feeds:
            try:
                list_of_articles = c.execute(\
                        "SELECT * FROM articles WHERE feed_link='" + \
                        feed[2] + "'").fetchall()
            except:
                continue
            sha1_hash = hashlib.sha1()
            sha1_hash.update(feed[2].encode('utf-8'))
            feed_id = sha1_hash.hexdigest()


            new_collection = {"feed_id" : feed_id.encode('utf-8'), \
                                "type": 0, \
                                "feed_image" : feed[3].encode('utf-8'), \
                                "feed_title" : feed[0].encode('utf-8'), \
                                "feed_link" : feed[2].encode('utf-8'), \
                                "site_link" : feed[1].encode('utf-8'), \
                                "mail" : feed[4]=="1"}
            

            mongo.add_collection(new_collection)

            
            if list_of_articles != []:
                # Walk through the list of articles for the current feed.
                articles = []
                for article in list_of_articles:
                    sha1_hash = hashlib.sha1()
                    sha1_hash.update(article[2].encode('utf-8'))
                    article_id = sha1_hash.hexdigest()


                    article = {"article_id": article_id.encode('utf-8'), \
                                "type":1, \
                                "article_date": article[0].encode('utf-8'), \
                                "article_link": article[2].encode('utf-8'), \
                                "article_title": article[1].encode('utf-8'), \
                                "article_content": article[3].encode('utf-8'), \
                                "article_readed": article[4]=="1", \
                                "article_like": article[6]=="1" \
                                }

                    articles.append(article)


                mongo.add_articles(articles, feed_id)

        c.close()


if __name__ == "__main__":
    load_feed()
#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2012/03/03 $"
__revision__ = "$Date: 2012/03/03 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

import time

import pymongo

class Articles(object):
    """
    """
    def __init__(self, url='localhost', port=27017):
        """
        Instantiates the connection.
        """
        self.connection = pymongo.connection.Connection(url, port)
        self.db = self.connection.pyaggr3g470r

    def add_collection(self, new_collection):
        """
        Creates a new collection for a new feed.
        """
        new_collection["type"] = 0
        
        name = str(new_collection["collection_id"])
        pymongo.collection.Collection(self.db, name)
        collection = self.db[name]
        collection.create_index([("article_link", pymongo.ASCENDING)], {"unique":True, "sparse":True})
        collection.insert(new_collection)

    def add_articles(self, articles, collection_id):
        """
        Add article(s) in a collection.
        """
        collection = self.db[str(collection_id)]
        for article in articles:
            article["type"] = 1
            cursor = collection.find({"article_id":article["article_id"]})
            if cursor.count() == 0:
                collection.insert(article)

    def get_all_articles(self):
        """
        Return all articles from all collections.
        """
        articles = []
        collections = self.db.collection_names()
        for collection_name in collections:
            collection = self.db[collection_name]
            articles.append(collection)
        return articles

    def get_articles_from_collection(self, collection_id):
        """
        Return all the articles of a collection.
        """
        collection = self.db[str(collection_id)]
        return collection
        
    def print_articles_from_collection(self, collection_id):
        """
        Print the articles of a collection.
        """
        collection = self.db[str(collection_id)]
        cursor = collection.find({"type":1})
        print "Article for the collection", collection_id
        for d in cursor:
            print d
            print
        
    def nb_users(self):
        """
        Return the number of users.
        """
        collection = self.db.users
        collection.count()

    def list_collections(self):
        """
        List all collections (feed).
        """
        collections = self.db.collection_names()
        return collections
    
    # Functions on database
    def drop_database(self):
        """
        Drop all the database
        """
        self.connection.drop_database('pyaggr3g470r')


if __name__ == "__main__":
    # Point of entry in execution mode.
    articles = Articles()


    # Create a collection for a stream
    collection_dic = {"collection_id": 42,\
                        "feed_image": "Image", \
                        "feed_title": "Title", \
                        "feed_link": "Link", \
                        "site_title": "Site link", \
                        "mail": True, \
                        }
    
    #articles.add_collection(collection_dic)


    
    # Add an article in the newly created collection
    article_dic1 = {"article_id": 51, \
                    "article_date": "Today", \
                    "article_link": "Link of the article", \
                    "article_title": "The title", \
                    "article_content": "The content of the article", \
                    "article_readed": True, \
                    "article_like": True \
                    }

    article_dic2 = {"article_id": 52, \
                    "article_date": "Yesterday", \
                    "article_link": "Link", \
                    "article_title": "Hello", \
                    "article_content": "The content of the article", \
                    "article_readed": True, \
                    "article_like": True \
                    }
    
    #articles.add_articles([article_dic1, article_dic2], 42)


    # Print articles of the collection
    articles.print_articles_from_collection("http://esr.ibiblio.org/?feed=rss2")

    
    print "All articles:"
    #print articles.get_all_articles()
    
    # Drop the database
    #articles.drop_database()
#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2012/03/03 $"
__date__ = "$Date: 2012/03/03 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

import time

from pymongo.connection import Connection

class Articles(object):
    """
    """
    def __init__(self, url='localhost', port=27017):
        """
        Instantiates the connection.
        """
        self.connection = Connection(url, port)
        self.db = self.connection.pyaggr3g470r

    def add_collection(self, collection):
        """
        Creates a new collection for a new feed.
        """
        collection =  self.db.collection.feed_id
        collection.insert(collection)

    def add_article(self, article, collection_id):
        """
        Add an article in a collection.
        """
        collection = self.db.collection_id
        cursor = collection.find({"article_id":article.article_id})
        if cursor.count() == 0:
            collection.insert(user_dic)

    def get_all_articles():
        """
        Return all articles from all collections.
        """
        articles = []
        collections = self.db.collection_names
        for colliection in collections:
            collection = self.db.collection_id
            articles.append(collection)
        return articles

    def get_articles_from_collection():
        """
        Return all the articles of a collection.
        """
        collection = self.db.collection_id
        return collection
        
        
        
    #
    # Collection: users
    #
    def register_user(self, sender_uuid, user):
        """
        Insert a new user in the collection of users.
        """
        user_dic = {"uuid":sender_uuid, "name":user, \
                    "time-registration":time.time()}

        collection = self.db.users
        cursor = collection.find({"uuid":sender_uuid})
        if cursor.count() == 0:
            collection.insert(user_dic)


    def print_users(self):
        """
        List and print the users.
        """
        collection = self.db.users
        cursor = collection.find()
        for d in cursor:
            print d

    def nb_users(self):
        """
        Return the number of users.
        """
        collection = self.db.users
        collection.count()


    # Functions on database
    def drop_wsc_database(self):
        self.connection.drop_database('pyaggr3g470r')


if __name__ == "__main__":
    # Point of entry in execution mode.
    articles_database = Articles()    
#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2012/01/06 $"
__date__ = "$Date: 2012/01/09 $"
__copyright__ = "Copyright (c) 2012 Public Research Centre Henri Tudor"
__license__ = ""

# http://127.0.0.1:28017/wisafecar/users
# http://www.mongodb.org/display/DOCS/Http+Interface#HttpInterface-SimpleRESTInterface


# https://github.com/kchodorow/sleepy.mongoose/wiki/
# Insertion of a message:
#     curl --data 'docs=[{"message":"traffic jam","position":"tampere"}]' 'http://10.13.1.157:27080/wisafecar/messages/_insert'
#
# Connecting:
#     https://github.com/kchodorow/sleepy.mongoose/wiki/Connecting
# Examples:
#     curl --data 'name=wsc' http://localhost:27080/_connect
#     GET http://localhost:27080/wisafecar/users/_find?name=wsc
# Filtering:
#     If we want to get all results for the client with id=d39fc988-376b-11e1-aa3b-0022680cb7e4:
#         urllib.quote('{"id":"d39fc988-376b-11e1-aa3b-0022680cb7e4"}')
#         http://127.0.0.1:27080/wisafecar/users/_find?criteria=%7B%22id%22%3A%22d39fc988-376b-11e1-aa3b-0022680cb7e4%22%7D
#           (urllib.quote skip special caracters.)
#    If we want to find all the traffic jams:
#         urllib.quote('{"message":"traffic_jam"}')
#         http://127.0.0.1:27080/wisafecar/messages/_find?criteria=%7B%22message%22%3A%22traffic_jam%22%7D

import time

from pymongo.connection import Connection

class MongoWSC(object):
    """
    """
    def __init__(self, url='localhost', port=27017):
        """
        Instantiates the connection.
        """
        self.connection = Connection(url, port)
        self.db = self.connection.wisafecar

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

    def get_users(self):
        """
        Return the list of users.
        """
        collection = self.db.users
        return collection

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

    #
    # Collection: messages
    #
    def log_message(self, sender_uuid, message):
        """
        Create a new message in the collection of messages.
        """
        message_dic = {"reporter":sender_uuid, "time":message[0], "lat":message[2].split(",")[1][:-1],
                        "long": message[2].split(",")[0][1:], "message":message[3]}

        collection = self.db.messages
        collection.insert(message_dic)

    def print_messages(self):
        """
        List and print the messages received by all the users.
        """
        collection = self.db.messages
        cursor = collection.find()
        for d in cursor:
            print d

    #
    # Collection: positions
    #
    def log_positions(self, sender_uuid, position):
        """
        Log a new position.
        """
        collection_dic = {"uuid":sender_uuid, "time":position[0], "lat":position[2].split(",")[1][:-1],
                        "long": position[2].split(",")[0][1:]}

        collection = self.db.positions
        collection.insert(collection_dic)

    def print_positions(self):
        """
        List and print the position updates of all the users.
        """
        collection = self.db.positions
        cursor = collection.find()
        for d in cursor:
            print d

    # Functions on database
    def drop_wsc_database(self):
        self.connection.drop_database('wisafecar')

if __name__ == "__main__":
    # Point of entry in execution mode.
    wsc_database = MongoWSC()
    print "Registered users:"
    wsc_database.print_users()

    print "\nPosition updates received:"
    wsc_database.print_positions()

    print "\nMessage received:"
    wsc_database.print_messages()

    print "\nDropping database..."
    wsc_database.drop_wsc_database()


    wsc_database.register_user("1d91f6fafe85", "Cedric")

    wsc_database.log_positions("1d91f6fafe85", [time.time(), "position", "(49.6229,6.18687)"])
    wsc_database.log_positions("1d91f6fafe85", [time.time(), "position", "(49.6228,6.18692)"])

    wsc_database.log_message("1d91f6fafe85", [time.time(), "alert", "(49.628,6.176)", "accident"])
    wsc_database.log_message("1d91f6fafe85", [time.time(), "alert", "(49.612,6.18689708)", "traffic_jam"])
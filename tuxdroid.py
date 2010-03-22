#! /usr/local/bin/python
#-*- coding: utf-8 -*-

"""Communication interface with Tux Droid.
"""

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2010/02/26 $"
__copyright__ = "Copyright (c) 2010 Cedric Bonhomme"
__license__ = "GPL v3"

import time
import sqlite3

try:
    from tuxisalive.api import *
except:
    raise NameError("The module tuxisalive is missing.")

class Tux(object):
    """Manage the connection with Tux Droid.
    """
    def __init__(self, locutor = "Julie "):
        """Connection to the server.
        """
        self.tux = TuxAPI('127.0.0.1', 270)
        self.tux.server.autoConnect(CLIENT_LEVEL_RESTRICTED, 'none', 'none')
        print "Connection with Tux Droid..."

        if not self.tux.server.waitConnected(10.0):
            raise Exception("The server of Tux Droid is not ready.")
        print "Connected to the server of Tux Droid."

        if not self.tux.dongle.waitConnected(10.0):
            raise Exception("Not connected to the dongle.")
        print "Connected to the dongle."

        if not self.tux.radio.waitConnected(10.0):
            raise Exception("Connection between Tux Droid and the dongle unpossible.")
        print "Tux Droid connected to the dongle."

        if self.tux.access.waitAcquire(10.0, ACCESS_PRIORITY_NORMAL):
            self.tux.tts.setLocutor(locutor) # set the locutor
            self.tux.tts.setPitch(110) # set the Pitch
            self.tux.tts.speakAsync("Hello")

    def disconnect(self):
        """Disconnect.
        """
        self.tux.server.disconnect()
        self.tux.destroy()

    def onStart(self):
        """
        """
        self.tux.flippers.onAsync(4, finalState = 'DOWN', speed = 3)
        self.tux.tts.speakAsync("Hello !")

    def say_something(self, message):
        """
        """
        self.tux.tts.speakAsync(message)

    def check_feeds(self):
        """
        """
        unread_articles = []
        try:
            conn = sqlite3.connect("./var/feed.db", isolation_level = None)
            c = conn.cursor()
            unread_articles = c.execute("SELECT * FROM articles WHERE article_readed='0'")
            c.close()
        except Exception, e:
            pass
        self.say_something("News to read !")
        #self.say_something(str(len(unread_articles)))
        #for unread_article in unread_articles:
            #self.say_something()


if __name__ == "__main__":
    # Point of entry in execution mode
    tux_reader = Tux()
    while True:
        time.sleep(10)
        tux_reader.check_feeds()
    tux_reader.disconnect()

#! /usr/bin/env python
# -*- coding: utf-8 -*-

# fetch.py
#
# You can use this script with cron, for example:
#  */30 * * * * cd ~/.pyaggr3g470r/ ; python fetch.py
# to fetch articles every 30 minutes.
import sys
import bootstrap
from pyaggr3g470r import crawler
from pyaggr3g470r.models import User

if __name__ == "__main__":
    # Point of entry in execution mode
    try:
        feed_id = int(sys.argv[2])
    except:
        feed_id = None

    users = []
    try:
        users = User.query.filter(User.email == sys.argv[1]).all()
    except:
        users = User.query.all()

    for user in users:
        if user.activation_key == "":
            print("Fetching articles for", user.nickname)
            feed_getter = crawler.FeedGetter(user.email)
            feed_getter.retrieve_feed(feed_id)

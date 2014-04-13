#! /usr/bin/env python
# -*- coding: utf-8 -*-

# fetch.py
#
# You can use this script with cron, for example:
#  */30 * * * * cd ~/.pyaggr3g470r/ ; python fetch.py
# to fetch articles every 30 minutes.

import sys
from pyaggr3g470r import feedgetter

if __name__ == "__main__":
    # Point of entry in execution mode
    try:
        feed_id = int(sys.argv[2])
    except:
        feed_id = None
    feed_getter = feedgetter.FeedGetter(sys.argv[1])
    feed_getter.retrieve_feed(feed_id)

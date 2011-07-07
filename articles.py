#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010  Cédric Bonhomme - http://cedricbonhomme.org/
#
# For more information : http://bitbucket.org/cedricbonhomme/pyaggr3g470r/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.2 $"
__date__ = "$Date: 2010/12/02 $"
__revisios__ = "$Date: 2011/07/07 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

from collections import OrderedDict

class Feed(object):
    """
    Represent a stream (RSS, ATOM, etc.).
    """
    def __init__(self):
        """
        Represent the components of a feed.
        """
        self.feed_id = ""
        self.feed_image = ""
        self.feed_title = ""
        self.feed_link = ""
        self.feed_site_link = ""
        self.mail = ""
        self.nb_articles = ""
        self.nb_unread_articles = ""
        self.articles = OrderedDict()

class Article(object):
    """
    Represent an article.
    """
    def __init__(self):
        """
        Represent the components of an article.
        """
        self.article_id = ""
        self.article_date = ""
        self.article_title = ""
        self.article_link = ""
        self.article_description = ""
        self.article_readed = ""
        self.like = ""
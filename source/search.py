#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2013  Cédric Bonhomme - http://cedricbonhomme.org/
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
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2010/06/24 $"
__revision__ = "$Date: 2013/06/24 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser

import conf
import utils
import mongodb

schema = Schema(title=TEXT(stored=True), \
                content=TEXT, \
                article_id=TEXT, \
                feed_id=TEXT)

def create_index():
    """
    """
    self.mongo = mongodb.Articles(conf.MONGODB_ADDRESS, conf.MONGODB_PORT, \
                        conf.MONGODB_DBNAME, conf.MONGODB_USER, conf.MONGODB_PASSWORD)
    feeds = self.mongo.get_all_feeds()
    ix = create_in("indexdir", schema)
    writer = ix.writer()
    for article in mongo.get_articles(feed["feed_id"], limit=10)
        writer.add_document(title=article["article_title"], \
                            content=utils.clear_string(article["article_content"]))
    writer.commit()


def search(index, term):
    """
    """
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(term)
        results = searcher.search(query)
        results[0]
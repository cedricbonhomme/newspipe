#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2013  Cédric Bonhomme - http://cedricbonhomme.org/
#
# For more information : https://bitbucket.org/cedricbonhomme/pyaggr3g470r/
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
__date__ = "$Date: 2013/06/24 $"
__revision__ = "$Date: 2013/06/25 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

import os

from whoosh.index import create_in, open_dir
from whoosh.index import EmptyIndexError
from whoosh.fields import *
from whoosh.query import *
from whoosh.qparser import QueryParser
from whoosh.writing import AsyncWriter

import conf
import utils

indexdir = "./var/indexdir"

schema = Schema(title=TEXT(stored=True), \
                content=TEXT, \
                article_id=TEXT(stored=True), \
                feed_id=TEXT(stored=True))

def create_index():
    """
    Creates the index.
    """
    mongo = mongodb.Articles(conf.MONGODB_ADDRESS, conf.MONGODB_PORT, \
                        conf.MONGODB_DBNAME, conf.MONGODB_USER, conf.MONGODB_PASSWORD)
    feeds = mongo.get_all_feeds()
    if not os.path.exists(indexdir):
        os.mkdir(indexdir)
    ix = create_in(indexdir, schema)
    writer = ix.writer()
    for feed in feeds:
        for article in mongo.get_articles(feed["feed_id"]):
            writer.add_document(title=article["article_title"], \
                                content=utils.clear_string(article["article_content"]), \
                                article_id=article["article_id"] , \
                                feed_id=feed["feed_id"])
    writer.commit()

def add_to_index(articles, feed):
    """
    Add a list of articles to the index.
    Here an AsyncWriter is used because the function will
    be called in multiple threads by the feedgetter module.
    """
    try:
        ix = open_dir(indexdir)
    except (EmptyIndexError, OSError) as e:
        raise EmptyIndexError
    writer = AsyncWriter(ix)
    for article in articles:
        writer.add_document(title=article["article_title"], \
                            content=utils.clear_string(article["article_content"]), \
                            article_id=article["article_id"] , \
                            feed_id=feed["feed_id"])
    writer.commit()

def delete_article(feed_id, article_id):
    """
    Delete an article from the index.
    """
    try:
        ix = open_dir(indexdir)
    except (EmptyIndexError, OSError) as e:
        raise EmptyIndexError
    writer = ix.writer()
    document = And([Term("feed_id", feed_id), Term("article_id", article_id)])
    writer.delete_by_query(document)
    writer.commit()

def search(term):
    """
    Search for `term` in the index.
    Returns a list of articles.
    """
    try:
        ix = open_dir(indexdir)
    except (EmptyIndexError, OSError) as e:
        raise EmptyIndexError
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(term)
        results = searcher.search(query, limit=None)
        return [(article["feed_id"], article["article_id"]) for article in results]

def nb_documents():
    """
    Return the number of undeleted documents.
    """
    try:
        ix = open_dir(indexdir)
    except (EmptyIndexError, OSError) as e:
        raise EmptyIndexError
    return ix.doc_count()

if __name__ == "__main__":
    # Point of entry in execution mode.
    #create_index()
    print(nb_documents())
    results = search("Nothomb")
    for article in results:
        print(article)

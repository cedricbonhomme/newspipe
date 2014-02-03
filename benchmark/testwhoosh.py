#! /usr/bin/env python
#-*- coding: utf-8 -*-


import os

from whoosh.index import create_in, open_dir
from whoosh.index import EmptyIndexError
from whoosh.fields import *
from whoosh.query import *
from whoosh.qparser import QueryParser

from pyaggr3g470r import utils

indexdir = "./pyaggr3g470r/var/indexdir"

schema = Schema(title=TEXT(stored=True), content=TEXT)

def create_index(articles):
    """
    Creates the index.
    """
    ix = create_in(indexdir, schema)
    writer = ix.writer()
    for article in articles:
        writer.add_document(content=utils.clear_string(article.content))
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
        #return [(article["feed_id"], article["article_id"]) for article in results]


if __name__ == "__main__":
    # Point of entry in execution mode.
    #create_index()
    print(nb_documents())
    results = search("Nothomb")
    for article in results:
        print(article)

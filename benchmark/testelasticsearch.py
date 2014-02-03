#! /usr/bin/env python
#-*- coding: utf-8 -*- 

import elasticsearch
from elasticsearch import client

from pyaggr3g470r import utils

# Connect to Elasticsearch node specified in the configuration file:
es = elasticsearch.Elasticsearch(hosts={"127.0.0.1" : 9200})

def delete_index():
    """
    Deletes all indexes.
    """
    es = elasticsearch.Elasticsearch(hosts={"127.0.0.1" : 9200})
    ic = client.IndicesClient(es.indices.client)
    try:
        ic.delete("")
    except:
        pass

def create_index(articles):
    """
    Creates the index.
    """
    for article in articles:
        res = es.index(
            index="pyaggr3g470r",
            doc_type="text",
            id=str(article.id),
            body={
                "title": article.title,
                "content": utils.clear_string(article.content)
            }
        )
    return True

def search(term):
    """
    Search a term.
    """
    try:
        es.search(index="pyaggr3g470r", body=
            {"query" : {
                    "filtered" : {
                        "query" : { 
                            "query_string" : { 
                                "default_field" : "content",
                                "query" : term
                            }
                        }
                    }
                }
            }, size=5000)
    except elasticsearch.exceptions.NotFoundError as e:
        pass
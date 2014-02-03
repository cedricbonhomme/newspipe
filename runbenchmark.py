#! /usr/bin/env python
#-*- coding: utf-8 -*- 


import time
from benchmark import testelasticsearch
from benchmark import testwhoosh

import conf
from pyaggr3g470r import models
models.connect(conf.DATABASE_NAME)

articles = models.Article.objects()



#
# Index generation
#

print "Indexes generation..."
# Whoosh
print "Whoosh"
begin = time.time()
testwhoosh.create_index(articles)
end = time.time()
print end - begin

print

# ElasticSearch
print "ElasticSearch"
testelasticsearch.delete_index()
begin = time.time()
testelasticsearch.create_index(articles)
end = time.time()
print end - begin



print
print
print



#
# Search
#
print "Search..."
for query in ["Edward Snowden", "Saint-Pierre-et-Miquelon", "micropatronage"]:
    print "Query:", query
    
    # Whoosh
    print "with Whoosh"
    for _ in range(5):
        begin = time.time()
        testwhoosh.search(query)
        end = time.time()
        print end - begin

    print

    # ElasticSearch
    print "with ElasticSearch"
    for _ in range(5):
        begin = time.time()
        testelasticsearch.search(query)
        end = time.time()
        print end - begin
        
    print
    print
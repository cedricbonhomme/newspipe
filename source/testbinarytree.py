# -*- coding: utf-8 -*-

import time
import sys
import resource
# Increases Python's recursion limit and the size of the stack.
resource.setrlimit(resource.RLIMIT_STACK, (2**29,-1))
sys.setrecursionlimit(10**6)

import mongodb
import binarytree

print("Loading articles from the database...")
database = mongodb.Articles()
begin = time.time()
articles = database.get_articles()
end = time.time()
print(("{} articles loaded in {} seconds.".format(len(articles), end-begin)))

print("Generating the binary tree...")
begin = time.time()
BTree = binarytree.CBOrdTree()
# add the root node (first article of the list)
root = BTree.addNode(articles[0])
for article in articles[1:]:
    BTree.insert(root, article)
end = time.time()
print(("Generation done in {0:2f} seconds.".format(end-begin)))

print("Maximum depth of the tree:")
print(BTree.maxDepth(root))
print("Oldest article:")
oldest_article = BTree.minValue(root)
print((oldest_article["article_date"].strftime('%Y-%m-%d %H:%M') + \
        " - " + oldest_article["article_title"]))
print("Newest article:")
newest_article = BTree.maxValue(root)
print((newest_article["article_date"].strftime('%Y-%m-%d %H:%M') + \
        " - " + newest_article["article_title"]))

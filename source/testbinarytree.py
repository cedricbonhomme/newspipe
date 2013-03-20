# -*- coding: utf-8 -*-

import time
import sys
import resource
# Increases Python's recursion limit and the size of the stack.
resource.setrlimit(resource.RLIMIT_STACK, (2**29,-1))
sys.setrecursionlimit(10**6)

import mongodb
import binarytree
import conf

print("Loading articles from the database...")
database = mongodb.Articles(conf.MONGODB_ADDRESS, conf.MONGODB_PORT, \
                            conf.MONGODB_DBNAME, conf.MONGODB_USER, \
                            conf.MONGODB_PASSWORD)
begin = time.time()
articles = database.get_articles()
end = time.time()
print(("{} articles loaded in {} seconds.".format(len(articles), end-begin)))

print("Generating the binary tree...")
begin = time.time()
tree = binarytree.OrderedBinaryTree()
# add the root node (first article of the list)
root = tree.addNode(articles[0])
for article in articles[1:]:
    tree.insert(root, article)
end = time.time()
print(("Generation done in {0:2f} seconds.".format(end-begin)))

print("Maximum depth of the tree:")
print(tree.maxDepth(root))
print("Oldest article:")
oldest_article = tree.minValue(root)
print((oldest_article["article_date"].strftime('%Y-%m-%d %H:%M') + \
        " - " + oldest_article["article_title"]))
print("Newest article:")
newest_article = tree.maxValue(root)
print((newest_article["article_date"].strftime('%Y-%m-%d %H:%M') + \
        " - " + newest_article["article_title"]))
print(tree)

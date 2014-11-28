#! /usr/bin/env python
#-*- coding: utf-8 -*-

import itertools
import utils


def compare_documents(feed):
    """
    Compare a list of documents by pair.
    """
    duplicates = []
    for pair in itertools.combinations(feed.articles, 2):
        if pair[0].content != "" and pair[0].content == pair[1].content:
            duplicates.append(pair)
    return duplicates
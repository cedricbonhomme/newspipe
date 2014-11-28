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
        if pair[0].content != "" and \
            (utils.clear_string(pair[0].title) == utils.clear_string(pair[1].title) or \
            utils.clear_string(pair[0].content) == utils.clear_string(pair[1].content)):
            duplicates.append(pair)
    return duplicates
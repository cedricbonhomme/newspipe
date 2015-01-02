#! /usr/bin/env python
#-*- coding: utf-8 -*-

import itertools
from datetime import timedelta

from pyaggr3g470r import utils

def compare_documents(feed):
    """
    Compare a list of documents by pair.
    """
    duplicates = []
    for pair in itertools.combinations(feed.articles, 2):
        date1 = pair[0].date
        date2 = pair[1].date
        if utils.clear_string(pair[0].title) == utils.clear_string(pair[1].title) and \
                                        (date1 - date2) < timedelta(days = 1):
            duplicates.append(pair)
    return duplicates
#! /usr/bin/env/python
# -*- coding: utf-8 -*-

import utils

class Search(object):
    """
    """
    def __init__(self):
        self.terms = {}

    def index(self):
        pass

    def search(self, word):
        result = []
        for term, texts in self.terms.items():
            if word in term:
                result.extend(text)
        return result
#! /usr/bin/env python
#-*- coding: utf-8 -*-

import itertools
import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer

import utils

# tokenizers/punkt/english.pickle


stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

def normalize(text):
    """
    Remove punctuation, lowercase, stem
    """
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

def cosine_sim(article1, article2):
    try:
        tfidf = vectorizer.fit_transform([utils.clear_string(article1.content),
                                        utils.clear_string(article2.content)])
    except ValueError as e:
        raise e
    return ((tfidf * tfidf.T).A)[0,1]


def compare_documents(feed):
    """
    Compare a list of documents by pair.
    """
    downloaded = nltk.download("punkt")
    if not downloaded:
        #  Ubuntu packaged version still uses old URL
        dl = nltk.downloader.Downloader("https://nltk.github.com/nltk_data/")
        dl.download("punkt")
    duplicates = []
    for pair in itertools.combinations(feed.articles, 2):
        try:
            result = cosine_sim(*pair)
            if abs(result.item() - 1.0) < 1e-10:
                duplicates.append(pair)
                #print pair[0].id, pair[0].title, pair[0].link
                #print pair[1].id, pair[1].title, pair[1].link
                #print
        except ValueError:
            continue
    return duplicates
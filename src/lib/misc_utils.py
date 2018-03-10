#! /usr/bin/env python
#-*- coding: utf-8 -*-

# Newspipe - A Web based news aggregator.
# Copyright (C) 2010-2016  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : https://github.com/newspipe/newspipe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 1.10 $"
__date__ = "$Date: 2010/12/07 $"
__revision__ = "$Date: 2016/11/22 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "AGPLv3"

import re
import os
import sys
import glob
import json
import logging
import operator
import urllib
import subprocess
import sqlalchemy
try:
    from urlparse import urlparse, parse_qs, urlunparse
except:
    from urllib.parse import urlparse, parse_qs, urlunparse, urljoin
from collections import Counter
from contextlib import contextmanager
from flask import request

import conf
from web.controllers import ArticleController
from lib.utils import clear_string

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = set(['xml', 'opml', 'json'])


def is_safe_url(target):
    """
    Ensures that a redirect target will lead to the same server.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def get_redirect_target():
    """
    Looks at various hints to find the redirect target.
    """
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


def allowed_file(filename):
    """
    Check if the uploaded file is allowed.
    """
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@contextmanager
def opened_w_error(filename, mode="r"):
    try:
        f = open(filename, mode)
    except IOError as err:
        yield None, err
    else:
        try:
            yield f, None
        finally:
            f.close()


def fetch(id, feed_id=None):
    """
    Fetch the feeds in a new processus.
    The default crawler ("asyncio") is launched with the manager.
    """
    cmd = [sys.executable, conf.BASE_DIR + '/manager.py', 'fetch_asyncio',
           '--user_id='+str(id)]
    if feed_id:
        cmd.append('--feed_id='+str(feed_id))
    return subprocess.Popen(cmd, stdout=subprocess.PIPE)


def history(user_id, year=None, month=None):
    """
    Sort articles by year and month.
    """
    articles_counter = Counter()
    articles = ArticleController(user_id).read()
    if None != year:
        articles = articles.filter(sqlalchemy.extract('year', 'Article.date') == year)
        if None != month:
            articles = articles.filter(sqlalchemy.extract('month', 'Article.date') == month)
    for article in articles.all():
        if None != year:
            articles_counter[article.date.month] += 1
        else:
            articles_counter[article.date.year] += 1
    return articles_counter, articles


def clean_url(url):
    """
    Remove utm_* parameters
    """
    parsed_url = urlparse(url)
    qd = parse_qs(parsed_url.query, keep_blank_values=True)
    filtered = dict((k, v) for k, v in qd.items()
                                        if not k.startswith('utm_'))
    return urlunparse([
        parsed_url.scheme,
        parsed_url.netloc,
        urllib.parse.quote(urllib.parse.unquote(parsed_url.path)),
        parsed_url.params,
        urllib.parse.urlencode(filtered, doseq=True),
        parsed_url.fragment
    ]).rstrip('=')


def load_stop_words():
    """
    Load the stop words and return them in a list.
    """
    stop_words_lists = glob.glob(os.path.join(conf.BASE_DIR,
                                                'web/var/stop_words/*.txt'))
    stop_words = []

    for stop_wods_list in stop_words_lists:
        with opened_w_error(stop_wods_list, "r") as (stop_wods_file, err):
            if err:
                stop_words = []
            else:
                stop_words += stop_wods_file.read().split(";")
    return stop_words


def top_words(articles, n=10, size=5):
    """
    Return the n most frequent words in a list.
    """
    stop_words = load_stop_words()
    words = Counter()
    wordre = re.compile(r'\b\w{%s,}\b' % size, re.I)
    for article in articles:
        for word in [elem.lower() for elem in
                wordre.findall(clear_string(article.content)) \
                if elem.lower() not in stop_words]:
            words[word] += 1
    return words.most_common(n)


def tag_cloud(tags):
    """
    Generates a tags cloud.
    """
    tags.sort(key=operator.itemgetter(0))
    max_tag = max([tag[1] for tag in tags])
    return '\n'.join([('<font size=%d>%s</font>' % \
        (min(1 + count * 7 / max_tag, 7), word)) for (word, count) in tags])

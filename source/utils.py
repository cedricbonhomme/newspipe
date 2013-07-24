#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2013  Cédric Bonhomme - http://cedricbonhomme.org/
#
# For more information : http://bitbucket.org/cedricbonhomme/pyaggr3g470r/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 1.4 $"
__date__ = "$Date: 2010/12/07 $"
__revision__ = "$Date: 2013/01/20 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

#
# This file provides functions used for:
# - the database management;
# - generation of tags cloud;
# - HTML processing;
# - e-mail notifications.
#

import os
import re
import glob
import operator
import calendar
import html.entities

try:
    from qrcode.pyqrnative.PyQRNative import QRCode, QRErrorCorrectLevel, CodeOverflowException
    from qrcode import qr
except:
    pass

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import urllib.request, urllib.error, urllib.parse
import http.server
from bs4 import BeautifulSoup

from collections import Counter

import conf

# regular expression to check URL
url_finders = [ \
    re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?/[-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]*[^]'\\.}>\\),\\\"]"), \
    re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?"), \
    re.compile("(~/|/|\\./)([-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]|\\\\)+"), \
    re.compile("'\\<((mailto:)|)[-A-Za-z0-9\\.]+@[-A-Za-z0-9\\.]+") \
]

def detect_url_errors(list_of_urls):
    """
    Detect URL errors.
    Return a list of error(s).
    """
    errors = []
    for url in list_of_urls:
        req = urllib.request.Request(url)
        try:
            urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            # server couldn't fulfill the request
            errors.append((url, e.code, \
                http.server.BaseHTTPRequestHandler.responses[e.code][1]))
        except urllib.error.URLError as e:
            # failed to reach the server
            errors.append((url, e.reason.errno ,e.reason.strerror))
    return errors

def generate_qr_code(article):
    """
    Generated a QR Code for the article given in parameter.
    """
    try:
        os.makedirs("./var/qrcode/")
    except OSError:
        pass
    if not os.path.isfile("./var/qrcode/" + article["article_id"] + ".png"):
        # QR Code generation
        try:
            f = qr.QRUrl(url = article["article_link"])
            f.make()
            f.save("./var/qrcode/" + article["article_id"] + ".png")
        except:
            pass

def clear_string(data):
    """
    Clear a string by removing HTML tags, HTML special caracters
    and consecutive white spaces (more that one).
    """
    p = re.compile(b'<[^>]+>') # HTML tags
    q = re.compile(b'\s') # consecutive white spaces
    return p.sub(b'', q.sub(b' ', bytes(data, "utf-8"))).decode("utf-8", "strict")

def normalize_filename(name):
    """
    Normalize a file name.
    """
    file_name = re.sub("[,'!?|&]", "", name)
    file_name = re.sub("[\s.]", "_", file_name)
    file_name = file_name.strip('_')
    file_name = file_name.strip('.')
    return os.path.normpath(file_name)

def load_stop_words():
    """
    Load the stop words and return them in a list.
    """
    stop_words_lists = glob.glob('./var/stop_words/*.txt')
    stop_words = []

    for stop_wods_list in stop_words_lists:
        with open(stop_wods_list, "r") as stop_wods_file:
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
                wordre.findall(clear_string(article["article_content"])) \
                if elem.lower() not in stop_words]:
            words[word] += 1
    return words.most_common(n)

def tag_cloud(tags, query="word_count"):
    """
    Generates a tags cloud.
    """
    tags.sort(key=operator.itemgetter(0))
    if query == "word_count":
        # tags cloud from the management page
        return ' '.join([('<font size=%d><a href="/search/?query=%s" title="Count: %s">%s</a></font>\n' % \
                    (min(1 + count * 7 / max([tag[1] for tag in tags]), 7), word, format(count, ',d'), word)) \
                        for (word, count) in tags])
    if query == "year":
        # tags cloud for the history
        return ' '.join([('<font size=%d><a href="/history/?query=%s:%s" title="Count: %s">%s</a></font>\n' % \
                        (min(1 + count * 7 / max([tag[1] for tag in tags]), 7), query, word, format(count, ',d'), word)) \
                            for (word, count) in tags])
    return ' '.join([('<font size=%d><a href="/history/?query=%s:%s" title="Count: %s">%s</a></font>\n' % \
                        (min(1 + count * 7 / max([tag[1] for tag in tags]), 7), query, word, format(count, ',d'), calendar.month_name[int(word)])) \
                            for (word, count) in tags])

def send_mail(mfrom, mto, feed_title, article_title, description):
    """
    Send the article via mail.
    """
    # Create the body of the message (a plain-text and an HTML version).
    html = """<html>\n<head>\n<title>%s</title>\n</head>\n<body>\n%s\n</body>\n</html>""" % \
                (feed_title + ": " + article_title, description)
    text = clear_string(description)

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '[pyAggr3g470r] ' + feed_title + ": " + article_title
    msg['From'] = mfrom
    msg['To'] = mto

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain', 'utf-8')
    part2 = MIMEText(html, 'html', 'utf-8')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    try:
        s = smtplib.SMTP(conf.smtp_server)
        s.login(conf.username, conf.password)
    except Exception as e:
        print(e)
    else:
        s.send_message(msg)
        s.quit()

def add_feed(feed_url):
    """
    Add the URL feed_url in the file feed.lst.
    """
    with open(conf.FEED_LIST, "r") as f:
        lines = f.readlines()
    lines = list(map(str.strip, lines))
    if feed_url in lines:
        return False
    lines.append(feed_url)
    with open(conf.FEED_LIST, "w") as f:
        f.write("\n".join(lines))
    return True

def change_feed_url(old_feed_url, new_feed_url):
    """
    Change the URL of a feed given in parameter.
    """
    # Replace the URL in the text file
    with open(conf.FEED_LIST, "r") as f:
        lines = f.readlines()
    lines = list(map(str.strip, lines))
    try:
        lines[lines.index(old_feed_url)] = new_feed_url
    except:
        return False
    with open(conf.FEED_LIST, "w") as f:
        f.write("\n".join(lines))
    return True

def remove_feed(feed_url):
    """
    Remove a feed from the file feed.lst and from the SQLite base.
    """
    with open(conf.FEED_LIST, "r") as f:
        lines = f.readlines()
    lines = list(map(str.strip, lines))
    try:
        del lines[lines.index(feed_url)]
    except:
        return False
    with open(conf.FEED_LIST, "w") as f:
        f.write("\n".join(lines))
    return True

def search_feed(url):
    """
    Search a feed in a HTML page.
    """
    soup = None
    try:
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page)
    except:
        return None
    feed_links = soup('link', type='application/atom+xml')
    feed_links.extend(soup('link', type='application/rss+xml'))
    for feed_link in feed_links:
        if url not in feed_link['href']:
            return urllib.parse.urljoin(url, feed_link['href'])
        return feed_link['href']
    return None

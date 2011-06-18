#! /usr/local/bin/python
#-*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010  Cédric Bonhomme - http://cedricbonhomme.org/
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
__version__ = "$Revision: 1.2 $"
__date__ = "$Date: 2010/12/07 $"
__revision__ = "$Date: 2011/04/15 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

import re
import hashlib
import sqlite3
import operator
import urlparse
import calendar
import unicodedata
import htmlentitydefs

import articles

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import urllib2
import BaseHTTPServer
from BeautifulSoup import BeautifulSoup

from datetime import datetime
from string import punctuation
from collections import Counter
from collections import OrderedDict

from StringIO import StringIO

import threading
LOCKER = threading.Lock()

import os
import ConfigParser
# load the configuration
config = ConfigParser.RawConfigParser()
config.read("./cfg/pyAggr3g470r.cfg")
path = os.path.abspath(".")
sqlite_base = os.path.abspath(config.get('global', 'sqlitebase'))
MAX_NB_ARTICLES = int(config.get('global', 'max_nb_articles'))
DIASPORA_POD = config.get('misc', 'diaspora_pod')
mail_from = config.get('mail','mail_from')
mail_to = config.get('mail','mail_to')
smtp_server = config.get('mail','smtp')
username =  config.get('mail','username')
password =  config.get('mail','password')

# regular expression to chech URL
url_finders = [ \
    re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?/[-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]*[^]'\\.}>\\),\\\"]"), \
    re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?"), \
    re.compile("(~/|/|\\./)([-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]|\\\\)+"), \
    re.compile("'\\<((mailto:)|)[-A-Za-z0-9\\.]+@[-A-Za-z0-9\\.]+"), \
]

def detect_url_errors(list_of_urls):
    """
    Detect URL errors.
    Return a list of error(s).
    """
    errors = []
    for url in list_of_urls:
        req = urllib2.Request(url)
        try:
            urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            # server couldn't fulfill the request
           errors.append((url, e.code, \
                BaseHTTPServer.BaseHTTPRequestHandler.responses[e.code][1]))
        except urllib2.URLError, e:
            # failed to reach the server
            errors.append((url, e.reason.errno ,e.reason.strerror))
    return errors

def clear_string(data):
    """
    Clear a string by removing HTML tags, HTML special caracters
    and consecutive white spaces (more that one).
    """
    p = re.compile(r'<[^<]*?/?>') # HTML tags
    q = re.compile(r'\s') # consecutive white spaces
    return p.sub('', q.sub(' ', data))

def unescape(text):
    """
    Removes HTML or XML character references and entities from a text string.
    """
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def not_combining(char):
    return unicodedata.category(char) != 'Mn'

def strip_accents(text, encoding):
    """
    Strip accents.

    >>> print strip_accents("déjà", "utf-8")
    deja
    """
    unicode_text= unicodedata.normalize('NFD', text.decode(encoding))
    return filter(not_combining, unicode_text).encode(encoding)

def normalize_filename(name):
    """
    Normalize a file name.
    """
    file_name = re.sub("[,'!?|&]", "", name)
    file_name = re.sub("[\s.]", "_", file_name)
    file_name = file_name.strip('_')
    file_name = file_name.strip('.')
    file_name = strip_accents(file_name, "utf-8")
    return os.path.normpath(file_name)

def top_words(feeds, n=10, size=5):
    """
    Return the n most frequent words in a list.
    """
    words = Counter()
    wordre = re.compile(r'\b\w{%s,}\b' % size, re.I)
    for feed in feeds.values():
        for article in feed.articles.values():
            for word in wordre.findall(clear_string(article.article_description)):
                words[word.lower()] += 1
    return words.most_common(n)

def tag_cloud(tags, query="word_count"):
    """
    Generates a tags cloud.
    """
    tags.sort(key=operator.itemgetter(0))
    if query == "word_count":
        # tags cloud from the management page
        return ' '.join([('<font size=%d><a href="/q/?querystring=%s" title="Count: %s">%s</a></font>\n' % \
                    (min(1 + count * 7 / max([tag[1] for tag in tags]), 7), word, count, word)) \
                        for (word, count) in tags])
    if query == "year":
        # tags cloud for the history
        return ' '.join([('<font size=%d><a href="/history/?querystring=%s:%s" title="Count: %s">%s</a></font>\n' % \
                        (min(1 + count * 7 / max([tag[1] for tag in tags]), 7), query, word, count, word)) \
                            for (word, count) in tags])
    return ' '.join([('<font size=%d><a href="/history/?querystring=%s:%s" title="Count: %s">%s</a></font>\n' % \
                        (min(1 + count * 7 / max([tag[1] for tag in tags]), 7), query, word, count, calendar.month_name[int(word)])) \
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
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    s = smtplib.SMTP(smtp_server)
    s.login(username, password)
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(mfrom, mto, msg.as_string())
    s.quit()

def string_to_datetime(stringtime):
    """
    Convert a string to datetime.
    """
    date, time = stringtime.split(' ')
    year, month, day = date.split('-')
    hour, minute, second = time.split(':')
    return datetime(year=int(year), month=int(month), day=int(day), \
        hour=int(hour), minute=int(minute), second=int(second))

def compare(stringtime1, stringtime2):
    """
    Compare two dates in the format 'yyyy-mm-dd hh:mm:ss'.
    """
    datetime1 = string_to_datetime(stringtime1)
    datetime2 = string_to_datetime(stringtime2)
    if datetime1 < datetime2:
        return -1
    elif datetime1 > datetime2:
        return 1
    return 0

def add_feed(feed_url):
    """
    Add the URL feed_url in the file feed.lst.
    """
    if os.path.exists("./var/feed.lst"):
        for line in open("./var/feed.lst", "r"):
            if feed_url in line:
                # if the feed is already in the file
                return False
    with open("./var/feed.lst", "a") as f:
        f.write(feed_url + "\n")
    return True

def change_feed_url(old_feed_url, new_feed_url):
    """
    Change the URL of a feed.
    """
    # Replace the URL in the text file
    with open("./var/feed.lst", "r") as f:
        lines = f.readlines()
    try:
        lines[lines.index(old_feed_url+"\n")] = new_feed_url + '\n'
    except:
        return
    with open("./var/feed.lst", "w") as f:
        f.write("\n".join(lines))

    # Replace the URL in the data base.
    try:
        conn = sqlite3.connect(sqlite_base, isolation_level = None)
        c = conn.cursor()
        c.execute("UPDATE articles SET feed_link='" + new_feed_url + "' WHERE feed_link='" + old_feed_url +"'")
        c.execute("UPDATE feeds SET feed_link='" + new_feed_url + "' WHERE feed_link='" + old_feed_url +"'")
        conn.commit()
        c.close()
    except Exception, e:
        print e

def remove_feed(feed_url):
    """
    Remove a feed from the file feed.lst and from the SQLite base.
    """
    feeds = []
    # Remove the URL from the file feed.lst
    if os.path.exists("./var/feed.lst"):
        for line in open("./var/feed.lst", "r"):
            if feed_url not in line:
                feeds.append(line.replace("\n", ""))
        with open("./var/feed.lst", "w") as f:
            f.write("\n".join(feeds) + "\n")
        # Remove articles from this feed from the SQLite base.
        try:
            conn = sqlite3.connect(sqlite_base, isolation_level = None)
            c = conn.cursor()
            c.execute("DELETE FROM feeds WHERE feed_link='" + feed_url +"'")
            c.execute("DELETE FROM articles WHERE feed_link='" + feed_url +"'")
            conn.commit()
            c.close()
        except:
            pass

def search_feed(url):
    """
    Search a feed in a HTML page.
    """
    soup = None
    try:
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
    except:
        return None
    feed_links = soup('link', type='application/atom+xml')
    feed_links.extend(soup('link', type='application/rss+xml'))
    for feed_link in feed_links:
        if url not in feed_link['href']:
            return urlparse.urljoin(url, feed_link['href'])
        return feed_link['href']
    return None

def create_base():
    """
    Create the base if not exists.
    """
    sqlite3.register_adapter(str, lambda s : s.decode('utf-8'))
    conn = sqlite3.connect(sqlite_base, isolation_level = None)
    c = conn.cursor()
    # table of feeds
    c.execute('''create table if not exists feeds
                (feed_title text, feed_site_link text, \
                feed_link text PRIMARY KEY, feed_image_link text,
                mail text)''')
    # table of articles
    c.execute('''create table if not exists articles
                (article_date text, article_title text, \
                article_link text PRIMARY KEY, article_description text, \
                article_readed text, feed_link text, like text)''')
    conn.commit()
    c.close()

def drop_base():
    """
    Delete all articles from the database.
    """
    sqlite3.register_adapter(str, lambda s : s.decode('utf-8'))
    conn = sqlite3.connect(sqlite_base, isolation_level = None)
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS feeds''')
    c.execute('''DROP TABLE IF EXISTS articles''')
    conn.commit()
    c.close()

def load_feed():
    """
    Load feeds and articles in a dictionary.
    """
    LOCKER.acquire()
    list_of_feeds = []
    list_of_articles = []
    try:
        conn = sqlite3.connect(sqlite_base, isolation_level = None)
        c = conn.cursor()
        list_of_feeds = c.execute("SELECT * FROM feeds").fetchall()
    except:
        pass

    nb_articles = 0
    nb_unread_articles = 0
    nb_mail_notifications = 0
    nb_favorites = 0

    # Contains the list of Feed object.
    feeds = OrderedDict()

    if list_of_feeds != []:
        sha1_hash = hashlib.sha1()
        # Case-insensitive sorting
        tupleList = [(x[0].lower(), x) for x in list_of_feeds]
        tupleList.sort(key=operator.itemgetter(0))

        # Walk through the list of feeds
        for feed in [x[1] for x in tupleList]:
            list_of_articles = c.execute(\
                    "SELECT * FROM articles WHERE feed_link='" + \
                    feed[2] + "'").fetchall()

            sha1_hash.update(feed[2].encode('utf-8'))
            feed_id = sha1_hash.hexdigest()

            # Current Feed object
            feed_object = articles.Feed()
            feed_object.feed_id = feed_id.encode('utf-8')
            feed_object.feed_title = feed[0].encode('utf-8')
            feed_object.feed_image = feed[3].encode('utf-8')
            feed_object.feed_link = feed[2].encode('utf-8')
            feed_object.feed_site_link = feed[1].encode('utf-8')
            feed_object.mail = feed[4]

            if list_of_articles != []:
                list_of_articles.sort(lambda x,y: compare(y[0], x[0]))
                if MAX_NB_ARTICLES != -1:
			list_of_articles = list_of_articles[:MAX_NB_ARTICLES]
                # Walk through the list of articles for the current feed.
                for article in list_of_articles:
                    sha1_hash.update(article[2].encode('utf-8'))
                    article_id = sha1_hash.hexdigest()

                    # Current Article object
                    article_object = articles.Article()
                    article_object.article_id = article_id.encode('utf-8')
                    article_object.article_date = article[0].encode('utf-8')
                    article_object.article_title = unescape(article[1]).encode('utf-8')
                    article_object.article_link = article[2].encode('utf-8')
                    article_object.article_description = unescape(article[3]).encode('utf-8')
                    article_object.article_readed = article[4]
                    article_object.like = article[6]

                    feed_object.articles[article_id] = article_object

                    # update the number of favorites articles
                    nb_favorites = nb_favorites + int(article[6])


                # informations about a feed
                feed_object.nb_articles = len(feed_object.articles)
                feed_object.nb_unread_articles = len([article for article in feed_object.articles.values() \
                                    if article.article_readed=="0"])

                feeds[feed_id] = feed_object

                nb_articles += feed_object.nb_articles
                nb_unread_articles += feed_object.nb_unread_articles
                nb_mail_notifications += int(feed_object.mail)

        c.close()
        LOCKER.release()
        return (feeds, nb_articles, nb_unread_articles, nb_favorites, nb_mail_notifications)
    LOCKER.release()
    return (feeds, nb_articles, nb_unread_articles, nb_favorites, nb_mail_notifications)

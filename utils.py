#! /usr/local/bin/python
#-*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010  Cédric Bonhomme - http://cedric.bonhomme.free.fr/
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
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2010/08/25 $"
__copyright__ = "Copyright (c) 2010 Cedric Bonhomme"
__license__ = "GPLv3"

IMPORT_ERROR = []

import re
import string
import hashlib
import sqlite3
import operator
import urlparse
import calendar
import htmlentitydefs

try:
    # for high performance on list
    from blist import *
except:
    pass

import smtplib
from email.mime.text import MIMEText

import urllib2
import BaseHTTPServer
from BeautifulSoup import BeautifulSoup

from datetime import datetime
from string import punctuation
from collections import Counter
from collections import OrderedDict

from StringIO import StringIO

try:
    from oice.langdet import langdet
    from oice.langdet import streams
    from oice.langdet import languages
except:
    IMPORT_ERROR.append("oice")

import threading
LOCKER = threading.Lock()

import os
import ConfigParser
# load the configuration
config = ConfigParser.RawConfigParser()
config.read("./cfg/pyAggr3g470r.cfg")
path = os.path.abspath(".")
sqlite_base = os.path.abspath(config.get('global', 'sqlitebase'))
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

def detect_language(text):
    """
    Detect the language of a text.
    English, French or other (not detected).
    """
    text = text.strip()
    try:
        text_stream = streams.Stream(StringIO(text))
        lang = langdet.LanguageDetector.detect(text_stream)
    except:
        return 'other'
    if lang == languages.french:
        return 'french'.encode('utf-8')
    elif lang == languages.english:
        return 'english'.encode('utf-8')
    else:
        return 'other'

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

def top_words(dic_articles, n=10, size=5):
    """
    Return the n most frequent words in a list.
    """
    words = Counter()
    wordre = re.compile(r'\b\w{%s,}\b' % size)
    for rss_feed_id in dic_articles.keys():
        for article in dic_articles[rss_feed_id]:
            for word in wordre.findall(clear_string(article[4].encode('utf-8'))):
                words[word.lower()] += 1
    return words.most_common(n)

def tag_cloud(tags, query="word_count"):
    """
    Generates a tags cloud.
    """
    tags.sort(key=operator.itemgetter(0))
    if query == "word_count":
        # tags cloud from the management page
        return ' '.join([('<font size="%d"><a href="/q/?querystring=%s" title="Count: %s">%s</a></font>\n' % \
                    (min(1 + count * 7 / max([tag[1] for tag in tags]), 7), word, count, word)) \
                        for (word, count) in tags])
    if query == "year":
        # tags cloud for the history
        return ' '.join([('<font size="%d"><a href="/history/?querystring=%s:%s" title="Count: %s">%s</a></font>\n' % \
                        (min(1 + count * 7 / max([tag[1] for tag in tags]), 7), query, word, count, word)) \
                            for (word, count) in tags])
    return ' '.join([('<font size="%d"><a href="/history/?querystring=%s:%s" title="Count: %s">%s</a></font>\n' % \
                        (min(1 + count * 7 / max([tag[1] for tag in tags]), 7), query, word, count, calendar.month_name[int(word)])) \
                            for (word, count) in tags])

def send_mail(mfrom, mto, feed_title, message):
    """Send the warning via mail
    """
    mail = MIMEText(message)
    mail['From'] = mfrom
    mail['To'] = mto
    mail['Subject'] = '[pyAggr3g470r] News from ' + feed_title
    #email['Text'] = message

    server = smtplib.SMTP(smtp_server)
    server.login(username, password)
    server.sendmail(mfrom, \
                    mto, \
                    mail.as_string())
    server.quit()

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

    # articles[feed_id] = (article_id, article_date, article_title,
    #               article_link, article_description, article_readed,
    #               article_language, like)
    # feeds[feed_id] = (nb_article, nb_article_unreaded, feed_image,
    #               feed_title, feed_link, feed_site_link, mail)
    articles, feeds = {}, OrderedDict()
    if list_of_feeds != []:
        sha1_hash = hashlib.sha1()
        # Case-insensitive sorting
        tupleList = [(x[0].lower(), x) for x in list_of_feeds]
        tupleList.sort(key=operator.itemgetter(0))

        for feed in [x[1] for x in tupleList]:
            list_of_articles = c.execute(\
                    "SELECT * FROM articles WHERE feed_link='" + \
                    feed[2] + "'").fetchall()

            sha1_hash.update(feed[2].encode('utf-8'))
            feed_id = sha1_hash.hexdigest()

            if list_of_articles != []:
                list_of_articles.sort(lambda x,y: compare(y[0], x[0]))
                for article in list_of_articles:
                    sha1_hash.update(article[2].encode('utf-8'))
                    article_id = sha1_hash.hexdigest()

                    # check the presence of the module for language detection
                    if "oice" not in IMPORT_ERROR:
                        if article[3] != "":
                            language = detect_language(clear_string(article[3][:80]).encode('utf-8') + \
                                                clear_string(article[1]).encode('utf-8'))
                        else:
                            language = detect_language(clear_string(article[1]).encode('utf-8'))
                    else:
                        language = "IMPORT_ERROR"

                    # informations about an article
                    article_list = [article_id, article[0], unescape(article[1]), \
                                    article[2], unescape(article[3]), \
                                    article[4], language, article[6]]

                    if feed_id not in articles:
                        try:
                            articles[feed_id] = blist([article_list])
                        except Exception:
                            articles[feed_id] = [article_list]
                    else:
                        articles[feed_id].append(article_list)

                # informations about a feed
                feeds[feed_id] = (len(articles[feed_id]), \
                                len([article for article in articles[feed_id] \
                                    if article[5]=="0"]), \
                                feed[3], feed[0], feed[2], feed[1] , feed[4]\
                                )

        c.close()
        LOCKER.release()
        return (articles, feeds)
    LOCKER.release()
    return (articles, feeds)
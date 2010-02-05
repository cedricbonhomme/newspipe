#! /usr/local/bin/python
#-*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.6 $"
__date__ = "$Date: 2010/02/05 $"
__copyright__ = "Copyright (c) 2010 Cedric Bonhomme"
__license__ = "GPLv3"

import sqlite3
import hashlib
import cherrypy
import ConfigParser

from datetime import datetime
from cherrypy.lib.static import serve_file

import feedgetter

config = ConfigParser.RawConfigParser()
config.read("./cfg/pyAggr3g470r.cfg")
path = config.get('global','path')

bindhost = "0.0.0.0"

cherrypy.config.update({ 'server.socket_port': 12556, 'server.socket_host': bindhost})

path = { '/css/style.css': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':path+'css/style.css'}}

htmlheader = """<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
                lang="en">\n<head>\n<link rel="stylesheet" type="text/css" href="/css/style.css"
                />\n<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n
                <title>pyAggr3g470r - RSS Feed Reader</title> </head>"""

htmlfooter =  """This software is under GPLv3 license. You are welcome to copy, modify or
                redistribute the source code according to the GPLv3 license.</div>
                </body></html>"""

htmlnav = """<body><h1><a name="top"><a href="/">pyAggr3g470r - RSS Feed Reader</a></a></h1><a
href="http://bitbucket.org/cedricbonhomme/pyaggr3g470r/" rel="noreferrer" target="_blank">
pyAggr3g470r (source code)</a>
"""


class Root:
    def index(self):
        """
        Main page containing the list of feeds and articles.
        """
        self.dic, self.dic_info = self.load_feed()
        html = htmlheader
        html += htmlnav
        html += """<div class="right inner">\n"""
        html += """<a href="/f/">Fetch all feeds</a>\n<br />\n"""
        html += """<a href="/m/">Management of feed</a>\n"""
        html += """<form method=get action="q/"><input type="text" name="v" value=""><input
        type="submit" value="search"></form>\n"""
        html += "<hr />\n"
        html += """Your feeds (%s):<br />\n""" % len(self.dic.keys())
        for rss_feed_id in self.dic.keys():

            html += """<a href="/#%s">%s</a> (<a href="/unread/%s"
                    title="Unread article(s)">%s</a> / %s)<br />\n""" % \
                                (rss_feed_id.encode('utf-8'), \
                                self.dic[rss_feed_id][0][5].encode('utf-8'), \
                                rss_feed_id, self.dic_info[rss_feed_id][1], \
                                self.dic_info[rss_feed_id][0])

        html += """</div>\n<div class="left inner">\n"""

        for rss_feed_id in self.dic.keys():
            html += '<h2><a name="' + rss_feed_id + '">' + \
                        '<a href="' + self.dic[rss_feed_id][0][6].encode('utf-8') + \
                        '"  rel="noreferrer" target="_blank">' + \
                        self.dic[rss_feed_id][0][5].encode('utf-8') + "</a></a></h2>\n"

            # The main page display only 10 articles by feeds.
            for article in self.dic[rss_feed_id][:10]:

                if article[7] == "0":
                    # not readed articles are in bold
                    not_read_begin = "<b>"
                    not_read_end = "</b>"
                else:
                    not_read_begin = ""
                    not_read_end = ""

                html += article[1].encode('utf-8') + \
                        not_read_begin + \
                        """ - <a href="/description/%s" rel="noreferrer" target="_blank">%s</a>""" % \
                                (article[0].encode('utf-8'), article[2].encode('utf-8')) + \
                        not_read_end + \
                        "<br />\n"
            html += "<br />\n"

            html += """<a href="/all_articles/%s">All articles</a>""" % (rss_feed_id,)
            if self.dic_info[rss_feed_id][1] != 0:
                html += """ <a href="/unread/%s" title="Unread article(s)"
                        >Unread article(s) (%s)</a>""" % (rss_feed_id, \
                                        self.dic_info[rss_feed_id][1])
            html += """<h4><a href="/#top">Top</a></h4>"""
            html += "<hr />\n"
        html += htmlfooter
        return html

    def m(self):
        """
        """
        return "Hello world !"

    def f(self):
        """
        Fetch all feeds
        """
        feed_getter = feedgetter.FeedGetter()
        feed_getter.retrieve_feed()
        return self.index()

    def description(self, article_id):
        """
        Display the description of an article in a new Web page.
        """
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">"""
        for rss_feed_id in self.dic.keys():
            for article in self.dic[rss_feed_id]:
                if article_id == article[0]:

                    if article[7] == "0":
                        self.mark_as_read(article[3]) # update the database
                        article[7] == 1 # avoids to reload self.dic

                    html += """<h1><i>%s</i> from <a href="/all_articles/%s">%s</a></h1><br />""" % \
                            (article[2].encode('utf-8'), rss_feed_id, article[5].encode('utf-8'))
                    description = article[4].encode('utf-8')
                    if description:
                        html += description
                    else:
                        html += "No description available."
                    html += """<hr />\n<a href="%s">Complete story</a>\n""" % (article[3].encode('utf-8'),)
        html += "<hr />\n" + htmlfooter
        return html

    def all_articles(self, feed_id):
        """
        Display all articles of a feed ('feed_title').
        """
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">"""
        html += """<h1>Articles of the feed %s</h1><br />""" % (self.dic[feed_id][0][5].encode('utf-8'))

        for article in self.dic[feed_id]:

            if article[7] == "0":
                # not readed articles are in bold
                not_read_begin = "<b>"
                not_read_end = "</b>"
            else:
                not_read_begin = ""
                not_read_end = ""

            html += article[1].encode('utf-8') + \
                    not_read_begin + \
                    """ - <a href="/description/%s" rel="noreferrer" target="_blank">%s</a>""" % \
                            (article[0].encode('utf-8'), article[2].encode('utf-8')) + \
                    not_read_end + \
                    "<br />\n"

        html += """<hr />\n<h4><a href="/">All feeds</a></h4>"""
        html += "<hr />\n"
        html += htmlfooter
        return html

    def unread(self, feed_id):
        """
        Display all unread articles of a feed ('feed_title').
        """
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">"""
        html += """<h1>Unread article(s) of the feed <a href="/all_articles/%s">%s</a></h1>
                <br />""" % (feed_id, self.dic[feed_id][0][5].encode('utf-8'))

        for article in self.dic[feed_id]:

            if article[7] == "0":

                html += article[1].encode('utf-8') + \
                        """ - <a href="/description/%s" rel="noreferrer" target="_blank">%s</a>""" % \
                                (article[0].encode('utf-8'), article[2].encode('utf-8')) + \
                        "<br />\n"

        html += """<hr />\n<h4><a href="/">All feeds</a></h4>"""
        html += "<hr />\n"
        html += htmlfooter
        return html

    def load_feed(self):
        """
        Load feeds in a dictionary.
        """
        list_of_articles = None
        try:
            conn = sqlite3.connect("./var/feed.db", isolation_level = None)
            c = conn.cursor()
            list_of_articles = c.execute("SELECT * FROM rss_feed").fetchall()
            c.close()
        except:
            pass

        # The key of dic is the id of the feed:
        # dic[feed_id] = (article_id, article_date, article_title,
        #               article_link, article_description, feed_title,
        #               feed_link, article_readed)
        # dic_info[feed_id] = (nb_article, nb_article_readed)
        dic, dic_info = {}, {}
        if list_of_articles is not None:
            for article in list_of_articles:
                sha256_hash = hashlib.sha256()
                sha256_hash.update(article[5].encode('utf-8'))
                feed_id = sha256_hash.hexdigest()
                sha256_hash.update(article[2].encode('utf-8'))
                article_id = sha256_hash.hexdigest()

                article_tuple = (article_id, article[0], article[1], \
                    article[2], article[3], article[4], article[5], article[6])

                if feed_id not in dic:
                    dic[feed_id] = [article_tuple]
                else:
                    dic[feed_id].append(article_tuple)

            # sort articles by date for each feeds
            for feeds in dic.keys():
                dic[feeds].sort(lambda x,y: compare(y[1], x[1]))

            for rss_feed_id in dic.keys():
                dic_info[rss_feed_id] = (len(dic.keys()), \
                                        len([article for article in dic[rss_feed_id] \
                                                                if article[7]=="0"]) \
                                        )

            return (dic, dic_info)
        return (dic, dic_info)

    def mark_as_read(self, article_link):
        """
        Mark an article as read by setting the value of the field
        'article_readed' of the SQLite database to 1.
        """
        try:
            conn = sqlite3.connect("./var/feed.db", isolation_level = None)
            c = conn.cursor()
            c.execute("UPDATE rss_feed SET article_readed=1 WHERE article_link='" + article_link + "'")
            conn.commit()
            c.close()



        except Exception, e:
            pass

    index.exposed = True
    m.exposed = True
    f.exposed = True
    description.exposed = True
    all_articles.exposed = True
    unread.exposed = True


def compare(stringtime1, stringtime2):
    """
    Compare two dates in the format 'yyyy-mm-dd hh:mm:ss'.
    """
    date1, time1 = stringtime1.split(' ')
    date2, time2 = stringtime2.split(' ')

    year1, month1, day1 = date1.split('-')
    year2, month2, day2 = date2.split('-')

    hour1, minute1, second1 = time1.split(':')
    hour2, minute2, second2 = time2.split(':')

    datetime1 = datetime(year=int(year1), month=int(month1), day=int(day1), \
                        hour=int(hour1), minute=int(minute1), second=int(second1))

    datetime2 = datetime(year=int(year2), month=int(month2), day=int(day2), \
                        hour=int(hour2), minute=int(minute2), second=int(second2))

    if datetime1 < datetime2:
        return -1
    elif datetime1 > datetime2:
        return 1
    else:
        return 0


if __name__ == '__main__':
    # Point of entry in execution mode
    root = Root()
    cherrypy.quickstart(root, config=path)
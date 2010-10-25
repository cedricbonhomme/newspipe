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
__version__ = "$Revision: 2.0 $"
__date__ = "$Date: 2010/09/03 $"
__copyright__ = "Copyright (c) 2010 Cedric Bonhomme"
__license__ = "GPLv3"

import os
import re
import time
import sqlite3
import cherrypy
import calendar
import threading

from collections import Counter

import utils
import feedgetter
import PyQRNative

bindhost = "0.0.0.0"

cherrypy.config.update({ 'server.socket_port': 12556, 'server.socket_host': bindhost})

# static files
path = {'/css/style.css': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'/css/style.css'}, \
        '/css/img/feed-icon-28x28.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'/css/img/feed-icon-28x28.png'}, \
        '/css/img/tuxrss.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'/css/img/tuxrss.png'}, \
        '/css/img/delicious.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'/css/img/delicious.png'}, \
        '/css/img/digg.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'/css/img/digg.png'}, \
        '/css/img/reddit.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'/css/img/reddit.png'}, \
        '/css/img/scoopeo.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'/css/img/scoopeo.png'}, \
        '/css/img/blogmarks.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'/css/img/blogmarks.png'}, \
        '/css/img/buzz.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'/css/img/buzz.png'}, \
        '/css/img/identica.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'/css/img/identica.png'}, \
        '/css/img/heart.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'/css/img/heart.png'}, \
        '/css/img/heart_open.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'/css/img/heart_open.png'}, \
        '/css/img/email-unread.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'/css/img/email-unread.png'}, \
        '/css/img/email-follow.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'/css/img/email-follow.png'}, \
        '/css/img/cross.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'/css/img/cross.png'}, \
        '/var/qrcode': {'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(utils.path, './var/qrcode')}}

def htmlheader(nb_unread_articles=""):
    """
    Return the header of the HTML page with the number of unread articles
    in the 'title' HTML tag..
    """
    return '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n' + \
        '<head>' + \
        '\n\t<title>'+ nb_unread_articles +'pyAggr3g470r - News aggregator</title>\n' + \
        '\t<link rel="stylesheet" type="text/css" href="/css/style.css" />' + \
        '\n\t<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n' + \
        '</head>\n'

htmlfooter = '<p>This software is under GPLv3 license. You are welcome to copy, modify or' + \
            ' redistribute the source code according to the' + \
            ' <a href="http://www.gnu.org/licenses/gpl-3.0.txt">GPLv3</a> license.</p></div>\n' + \
            '</body>\n</html>'

htmlnav = '<body>\n<h1><div class="right innerlogo"><a href="/"><img src="/css/img/tuxrss.png"' + \
        """ title="What's new today?"/></a>""" + \
        '</div><a name="top"><a href="/">pyAggr3g470r - News aggregator</a></a></h1>\n<a' + \
        ' href="http://bitbucket.org/cedricbonhomme/pyaggr3g470r/" rel="noreferrer" target="_blank">' + \
        'pyAggr3g470r (source code)</a>'


class Root:
    """
    Root class.
    All pages of pyAggr3g470r are described in this class.
    """
    def index(self):
        """
        Main page containing the list of feeds and articles.
        """
        # if there are unread articles, display the number in the tab
        html = htmlheader((self.nb_unread_articles and \
                            ['(' + str(self.nb_unread_articles) +') '] or \
                            [""])[0])
        html += htmlnav
        html += self.create_right_menu()
        html += """<div class="left inner">\n"""

        if self.articles:
            html += """<a href="/list_favorites/"><img src="/css/img/heart.png" title="Your favorites (%s)" /></a>\n""" % \
                (self.nb_favorites,)

            html += """<a href="/list_notification"><img src="/css/img/email-follow.png" title="Active e-mail notifications (%s)" /></a>\n""" % \
                (self.nb_mail_notifications,)

            if self.nb_unread_articles != 0:
                html += """<a href="/unread/All"><img src="/css/img/email-unread.png" title="Unread article(s): %s" /></a>\n""" % \
                    (self.nb_unread_articles,)


        # The main page display all the feeds.
        for rss_feed_id in self.feeds.keys():
            html += """<h2><a name="%s"><a href="%s" rel="noreferrer"
                    target="_blank">%s</a></a>
                    <a href="%s" rel="noreferrer"
                    target="_blank"><img src="%s" width="28" height="28" /></a></h2>\n""" % \
                        (rss_feed_id, \
                        self.feeds[rss_feed_id][5].encode('utf-8'), \
                        self.feeds[rss_feed_id][3].encode('utf-8'), \
                        self.feeds[rss_feed_id][4].encode('utf-8'), \
                        self.feeds[rss_feed_id][2].encode('utf-8'))

            # The main page display only 10 articles by feeds.
            for article in self.articles[rss_feed_id][:10]:

                if article[5] == "0":
                    # not readed articles are in bold
                    not_read_begin = "<b>"
                    not_read_end = "</b>"
                else:
                    not_read_begin = ""
                    not_read_end = ""

                # display a heart for faved articles
                if article[7] == "1":
                    like = """ <img src="/css/img/heart.png" title="I like this article!" />"""
                else:
                    like = ""

                # title of the article
                html += article[1].encode('utf-8') + \
                        " - " + not_read_begin + \
                        """<a href="/description/%s:%s" rel="noreferrer" target="_blank">%s</a>""" % \
                                (rss_feed_id, article[0].encode('utf-8'), article[2].encode('utf-8')[:150]) + \
                        not_read_end + like + \
                        "<br />\n"
            html += "<br />\n"

            # some options for the current feed
            html += """<a href="/all_articles/%s">All articles</a>&nbsp;&nbsp;&nbsp;""" % (rss_feed_id,)
            html += """&nbsp;&nbsp;<a href="/mark_as_read/Feed_FromMainPage:%s">Mark all as read</a>""" % (rss_feed_id,)
            if self.feeds[rss_feed_id][1] != 0:
                html += """&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="/unread/%s" title="Unread article(s)"
                        >Unread article(s) (%s)</a>""" % (rss_feed_id, \
                                        self.feeds[rss_feed_id][1])
            if self.feeds[rss_feed_id][6] == "0":
                html += """<br />\n<a href="/mail_notification/start:%s" title="By e-mail">Stay tuned</a>""" % (rss_feed_id,)
            else:
                html += """<br />\n<a href="/mail_notification/stop:%s" title="By e-mail">Stop staying tuned</a>""" %  (rss_feed_id,)
            html += """<h4><a href="/#top">Top</a></h4>"""
            html += "<hr />\n"
        html += htmlfooter
        return html

    index.exposed = True


    def create_right_menu(self):
        """
        Create the right menu.
        """
        html = """<div class="right inner">\n"""
        html += """<a href="/management/">Management</a><br />\n"""
        html += """<a href="/history/">History</a><br />\n"""
        html += """<a href="/fetch/">Fetch all feeds</a><br />\n"""
        html += """<a href="/mark_as_read/All:">Mark articles as read</a>\n"""
        html += """<form method=get action="/q/"><input type="text" name="querystring" value=""><input
        type="submit" value="Search"></form>\n"""
        html += "<hr />\n"
        # insert the list of feeds in the menu
        html += self.create_list_of_feeds()
        html += "</div>\n"

        return html

    def create_list_of_feeds(self):
        """
        Create the list of feeds.
        """
        html = """<div class="nav_container">Your feeds (%s):<br />\n""" % len(self.articles.keys())
        for rss_feed_id in self.feeds.keys():
            if self.feeds[rss_feed_id][1] != 0:
                # not readed articles are in bold
                not_read_begin = "<b>"
                not_read_end = "</b>"
            else:
                not_read_begin = ""
                not_read_end = ""
            html += """<div><a href="/#%s">%s</a> (<a href="/unread/%s"
                    title="Unread article(s)">%s%s%s</a> / %s)</div>""" % \
                            (rss_feed_id.encode('utf-8'), \
                            self.feeds[rss_feed_id][3].encode('utf-8'), \
                            rss_feed_id, not_read_begin, \
                            self.feeds[rss_feed_id][1], not_read_end, \
                            self.feeds[rss_feed_id][0])

        return "</div>" + html


    def management(self, word_size=6):
        """
        Management of articles.
        """
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">\n"""
        html += "<h1>Add Feeds</h1>\n"
        html += """<form method=get action="/add_feed/"><input type="text" name="url" value="">\n<input
        type="submit" value="OK"></form>\n"""

        if self.articles:
            html += "<h1>Delete Feeds</h1>\n"
            html += """<form method=get action="/remove_feed/"><select name="feed_id">\n"""
            for feed_id in self.feeds.keys():
                html += """\t<option value="%s">%s</option>\n""" % \
                        (feed_id, self.feeds[feed_id][3].encode('utf-8'))
            html += """</select><input type="submit" value="OK"></form>\n"""
            html += """<p>Active e-mail notifications: <a href="/list_notification">%s</a></p>\n""" % \
                        (self.nb_mail_notifications,)
            html += """<p>You like <a href="/list_favorites/">%s</a> article(s).</p>\n""" % \
                        (self.nb_favorites, )

        html += "<hr />\n"

        # Informations about the data base of articles, export funtions...
        html += """<p>The database contains a total of %s article(s) with
                <a href="/unread/All">%s unread article(s)</a>.<br />""" % \
                    (self.nb_articles, self.nb_unread_articles)
        html += """Database: %s.\n<br />Size: %s bytes.</p>\n""" % \
                    (os.path.abspath(utils.sqlite_base), os.path.getsize(utils.sqlite_base))

        html += """<form method=get action="/fetch/">\n<input type="submit" value="Fetch all feeds"></form>\n"""
        html += """<form method=get action="/drop_base">\n<input type="submit" value="Delete all articles"></form>\n"""
        html += "<h1>Export articles</h1>\n\n"
        html += """<form method=get action="/export/"><select name="export_method">\n"""
        html += """\t<option value="export_HTML" selected='selected'>HTML</option>\n"""
        html += """\t<option value="export_TXT">Text</option>\n"""
        html += """</select><input type="submit" value="Export"></form>\n"""

        html += "<hr />\n\n"

        # Some statistics
        if self.articles:
            self.top_words = utils.top_words(self.articles, n=50, size=int(word_size))
            html += "<h1>Statistics</h1>\n<br />\n"
            if "oice" not in utils.IMPORT_ERROR:
                # counter object to count the number of
                # french and english articles
                counter = Counter()
                for rss_feed_id in self.articles.keys():
                    for article in self.articles[rss_feed_id]:
                        counter[article[6]] += 1

            # Tags cloud
            html += "Minimum size of a word: "
            html += """<form method=get action="/management/"><select name="word_size">\n"""
            for size in range(1, 16):
                if size == int(word_size):
                    select = " selected='selected'"
                else:
                    select = ""
                html += """\t<option value="%s" %s>%s</option>\n""" % (size, select, size)
            html += """</select><input type="submit" value="OK"></form>\n"""
            html += "<br /><h3>Tag cloud</h3>\n"
            html += '<div style="width: 35%; overflow:hidden; text-align: justify">' + \
                        utils.tag_cloud(self.top_words) + '</div>'

            # Languages
            html += "<br /><h3>Languages</h3>\n"
            if "oice" in utils.IMPORT_ERROR:
                html += "Install the module "
                html += """<a href="http://pypi.python.org/pypi/oice.langdet/">oice.langdet</a>"""
            else:
                html += "<ul>\n"
                for language in ['english', 'french']:
                    html += """\t<li>%s articles in <a href="/language/%s">%s</a></li>\n""" % \
                                    (counter[language], language, language)
                html += "</ul>\n<br />"

            html += "<hr />\n"
        html += htmlfooter
        return html

    management.exposed = True


    def q(self, querystring=None):
        """
        Search for a feed. Simply search for the string 'querystring'
        in the description of the article.
        """
        param, _, value = querystring.partition(':')
        wordre = re.compile(r'\b%s\b' % param, re.I)
        feed_id = None
        if param == "Feed":
            feed_id, _, querystring = value.partition(':')
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""

        html += """<h1>Articles containing the string <i>%s</i></h1><br />""" % (querystring,)

        if feed_id is not None:
            for article in self.articles[rss_feed_id]:
                article_content = utils.clear_string(article[4].encode('utf-8'))
                if not article_content:
                    utils.clear_string(article[2].encode('utf-8'))
                if wordre.findall(article_content) != []:
                    if article[5] == "0":
                        # not readed articles are in bold
                        not_read_begin = "<b>"
                        not_read_end = "</b>"
                    else:
                        not_read_begin = ""
                        not_read_end = ""

                    html += article[1].encode('utf-8') + \
                            " - " + not_read_begin + \
                            """<a href="/description/%s:%s" rel="noreferrer" target="_blank">%s</a>""" % \
                                    (feed_id, article[0].encode('utf-8'), article[2].encode('utf-8')) + \
                            not_read_end + """<br />\n"""
        else:
            for rss_feed_id in self.articles.keys():
                new_feed_section = True
                for article in self.articles[rss_feed_id]:
                    article_content = utils.clear_string(article[4].encode('utf-8'))
                    if not article_content:
                        utils.clear_string(article[2].encode('utf-8'))
                    if wordre.findall(article_content) != []:
                        if new_feed_section is True:
                            new_feed_section = False
                            html += """<h2><a name="%s"><a href="%s" rel="noreferrer"
                            target="_blank">%s</a></a>
                            <a href="%s" rel="noreferrer"
                            target="_blank"><img src="%s" width="28" height="28" /></a></h2>\n""" % \
                                (rss_feed_id, \
                                self.feeds[rss_feed_id][5].encode('utf-8'), \
                                self.feeds[rss_feed_id][3].encode('utf-8'), \
                                self.feeds[rss_feed_id][4].encode('utf-8'), \
                                self.feeds[rss_feed_id][2].encode('utf-8'))

                        if article[5] == "0":
                            # not readed articles are in bold
                            not_read_begin = "<b>"
                            not_read_end = "</b>"
                        else:
                            not_read_begin = ""
                            not_read_end = ""

                        html += article[1].encode('utf-8') + \
                                " - " + not_read_begin + \
                                """<a href="/description/%s:%s" rel="noreferrer" target="_blank">%s</a>""" % \
                                        (rss_feed_id, article[0].encode('utf-8'), article[2].encode('utf-8')) + \
                                not_read_end + """<br />\n"""
        html += "<hr />"
        html += htmlfooter
        return html

    q.exposed = True


    def fetch(self):
        """
        Fetch all feeds
        """
        feed_getter = feedgetter.FeedGetter()
        feed_getter.retrieve_feed()
        return self.index()

    fetch.exposed = True


    def description(self, param):
        """
        Display the description of an article in a new Web page.
        """
        try:
            feed_id, article_id = param.split(':')
        except:
            return self.error_page("Bad URL")
        try:
            articles_list = self.articles[feed_id]
        except KeyError:
            return self.error_page("This feed do not exists.")
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        for article in articles_list:
            if article_id == article[0]:

                try:
                    os.makedirs("./var/qrcode/")
                except OSError:
                    pass
                if not os.path.isfile("./var/qrcode/"+article_id+".png"):
                    # QR code generation
                    try:
                        qr = PyQRNative.QRCode(7, PyQRNative.QRErrorCorrectLevel.L)
                        qr.addData(article[3])
                        qr.make()
                        im = qr.makeImage()
                        im.save("./var/qrcode/"+article_id+".png", format='png')
                    except Exception, e:
                        # Code length overflow
                        print e

                if article[5] == "0":
                    self.mark_as_read("Article:"+article[3]) # update the database

                html += '\n<div style="width: 50%; overflow:hidden; text-align: justify; margin:0 auto">\n'
                html += """<h1><i>%s</i> from <a href="/all_articles/%s">%s</a></h1>\n<br />\n""" % \
                                (article[2].encode('utf-8'), feed_id, \
                                self.feeds[feed_id][3].encode('utf-8'))
                if article[7] == "1":
                    html += """<a href="/like/no:%s:%s"><img src="/css/img/heart.png" title="I like this article!" /></a>""" % \
                                (feed_id, article_id)
                else:
                    html += """<a href="/like/yes:%s:%s"><img src="/css/img/heart_open.png" title="Click if you like this article." /></a>""" % \
                                (feed_id, article_id)
                html += """&nbsp;&nbsp;<a href="/delete_article/%s:%s"><img src="/css/img/cross.png" title="Delete this article" /></a>""" % \
                                (feed_id, article_id)
                html += "<br /><br />"
                description = article[4]
                if description:
                    html += description.encode('utf-8')
                else:
                    html += "No description available."
                html += "\n</div>\n<hr />\n"
                html += """This article seems to be written in <a href="/language/%s">%s</a>.\n""" % \
                                (article[6], article[6])
                html += """<br />\n<a href="/plain_text/%s:%s">Plain text</a>\n""" % \
                                (feed_id, article_id)
                html += """<br />\n<a href="%s">Complete story</a>\n<br />\n""" % \
                                (article[3].encode('utf-8'),)
                # Share this article:
                # on Identi.ca
                html += """\n<a href="http://identi.ca/index.php?action=newnotice&status_textarea=%s: %s" title="Share on Identi.ca" target="_blank"><img src="/css/img/identica.png" /></a> &nbsp;&nbsp; \n""" % \
                                (article[2].encode('utf-8'), article[3].encode('utf-8'))

                # on Google Buzz
                html += """\n\n<a href="http://www.google.com/buzz/post?url=%s&message=%s"
                        rel="noreferrer" target="_blank">\n\t
                        <img src="/css/img/buzz.png" title="Share on Google Buzz" /></a> &nbsp;&nbsp; """ % \
                                (article[3].encode('utf-8'), article[2].encode('utf-8'))

                # on delicious
                html += """\n\n<a href="http://delicious.com/post?url=%s&title=%s"
                        rel="noreferrer" target="_blank">\n\t
                        <img src="/css/img/delicious.png" title="Share on del.iciou.us" /></a> &nbsp;&nbsp; """ % \
                                (article[3].encode('utf-8'), article[2].encode('utf-8'))

                # on Digg
                html += """\n\n<a href="http://digg.com/submit?url=%s&title=%s"
                        rel="noreferrer" target="_blank">\n\t
                        <img src="/css/img/digg.png" title="Share on Digg" /></a> &nbsp;&nbsp; """ % \
                                (article[3].encode('utf-8'), article[2].encode('utf-8'))
                # on reddit
                html += """\n\n<a href="http://reddit.com/submit?url=%s&title=%s"
                        rel="noreferrer" target="_blank">\n\t
                        <img src="/css/img/reddit.png" title="Share on reddit" /></a> &nbsp;&nbsp; """ % \
                                (article[3].encode('utf-8'), article[2].encode('utf-8'))
                # on Scoopeo
                html += """\n\n<a href="http://scoopeo.com/scoop/new?newurl=%s&title=%s"
                        rel="noreferrer" target="_blank">\n\t
                        <img src="/css/img/scoopeo.png" title="Share on Scoopeo" /></a> &nbsp;&nbsp; """ % \
                                (article[3].encode('utf-8'), article[2].encode('utf-8'))
                # on Blogmarks
                html += """\n\n<a href="http://blogmarks.net/my/new.php?url=%s&title=%s"
                        rel="noreferrer" target="_blank">\n\t
                        <img src="/css/img/blogmarks.png" title="Share on Blogmarks" /></a> &nbsp;&nbsp; """ % \
                                (article[3].encode('utf-8'), article[2].encode('utf-8'))

                # on Twitter
                html += """\n\n<a href="http://twitter.com/share" class="twitter-share-button" data-url="%s" data-text="%s" data-count="horizontal">Tweet</a><script type="text/javascript" src="http://platform.twitter.com/widgets.js"></script>\n""" % \
                                (article[3].encode('utf-8'), article[2].encode('utf-8'))

                # on Google Buzz with counter
                html += """<br /><br />\n<a title="Share on Google Buzz" class="google-buzz-button" href="http://www.google.com/buzz/post" data-button-style="normal-count" data-url="%s"></a><script type="text/javascript" src="http://www.google.com/buzz/api/button.js"></script>\n &nbsp;&nbsp; """ % \
                                (article[3].encode('utf-8'),)

                html += """<br />\n<img src="/var/qrcode/%s.png" title="Share with your smartphone" />""" % \
                                (article_id,)
                break
        html += "<hr />\n" + htmlfooter
        return html

    description.exposed = True


    def all_articles(self, feed_id):
        """
        Display all articles of a feed.
        """
        try:
            articles_list = self.articles[feed_id]
        except KeyError:
            return self.error_page("This feed do not exists.")
        html = htmlheader()
        html += htmlnav
        html += """<div class="right inner">\n"""
        html += """<a href="/mark_as_read/Feed:%s">Mark all articles from this feed as read</a>""" % (feed_id,)
        html += """<br />\n<form method=get action="/q/Feed"><input type="text" name="Feed:%s:querystring" value=""><input
        type="submit" value="Search this feed"></form>\n""" % (feed_id,)
        html += "<hr />\n"
        html += self.create_list_of_feeds()
        html += """</div> <div class="left inner">"""
        html += """<h1>Articles of the feed <i>%s</i></h1><br />""" % (self.feeds[feed_id][3].encode('utf-8'))

        for article in articles_list:

            if article[5] == "0":
                # not readed articles are in bold
                not_read_begin = "<b>"
                not_read_end = "</b>"
            else:
                not_read_begin = ""
                not_read_end = ""

            if article[7] == "1":
                like = """ <img src="/css/img/heart.png" title="I like this article!" />"""
            else:
                like = ""

            html += article[1].encode('utf-8') + \
                    " - " + not_read_begin + \
                    """<a href="/description/%s:%s" rel="noreferrer" target="_blank">%s</a>""" % \
                            (feed_id, article[0].encode('utf-8'), \
                            utils.clear_string(article[2].encode('utf-8'))) + \
                    not_read_end + like + \
                    "<br />\n"

        html += """\n<h4><a href="/">All feeds</a></h4>"""
        html += "<hr />\n"
        html += htmlfooter
        return html

    all_articles.exposed = True


    def unread(self, feed_id):
        """
        Display all unread articles of a feed.
        """
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        if self.nb_unread_articles != 0:
            if feed_id == "All":
                html += "<h1>Unread article(s)</h1>"
                html += """\n<br />\n<a href="/mark_as_read/All:">Mark articles as read</a>\n<hr />\n"""
                for rss_feed_id in self.feeds.keys():
                    new_feed_section = True
                    nb_unread = 0
                    for article in self.articles[rss_feed_id]:
                        if article[5] == "0":
                            nb_unread += 1
                            if new_feed_section is True:
                                new_feed_section = False
                                html += """<h2><a name="%s"><a href="%s" rel="noreferrer"
                                target="_blank">%s</a></a>
                                <a href="%s" rel="noreferrer"
                                target="_blank"><img src="%s" width="28" height="28" /></a></h2>\n""" % \
                                    (rss_feed_id, \
                                    self.feeds[rss_feed_id][5].encode('utf-8'), \
                                    self.feeds[rss_feed_id][3].encode('utf-8'), \
                                    self.feeds[rss_feed_id][4].encode('utf-8'), \
                                    self.feeds[rss_feed_id][2].encode('utf-8'))

                            html += article[1].encode('utf-8') + \
                                    """ - <a href="/description/%s:%s" rel="noreferrer" target="_blank">%s</a><br />\n""" % \
                                            (rss_feed_id, article[0].encode('utf-8'), \
                                            article[2].encode('utf-8'))

                            if nb_unread == self.feeds[rss_feed_id][1]:
                                html += """<br />\n<a href="/mark_as_read/Feed:%s">Mark all articles from this feed as read</a>\n""" % \
                                            (rss_feed_id,)
                html += """<hr />\n<a href="/mark_as_read/All:">Mark articles as read</a>\n"""
            else:
                try:
                    articles_list = self.articles[feed_id]
                except KeyError:
                    return self.error_page("This feed do not exists.")
                html += """<h1>Unread article(s) of the feed <a href="/all_articles/%s">%s</a></h1>
                    <br />""" % (feed_id, self.feeds[feed_id][3].encode('utf-8'))
                for article in articles_list:
                    if article[5] == "0":
                        html += article[1].encode('utf-8') + \
                                """ - <a href="/description/%s:%s" rel="noreferrer" target="_blank">%s</a>""" % \
                                        (feed_id, article[0].encode('utf-8'), article[2].encode('utf-8')) + \
                                "<br />\n"
                html += """<hr />\n<a href="/mark_as_read/Feed:%s">Mark all as read</a>""" % (feed_id,)
        else:
            html += "<h1>No unread article(s)</h1>"
        html += """\n<h4><a href="/">All feeds</a></h4>"""
        html += "<hr />\n"
        html += htmlfooter
        return html

    unread.exposed = True


    def language(self, lang):
        """
        Display articles by language.
        """
        if lang not in ['english', 'french', 'other']:
            return self.error_page('This language is not supported.')
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        html += """<h1>Article(s) written in %s</h1>\n<br />\n""" % (lang,)
        if "oice" not in utils.IMPORT_ERROR:
            for rss_feed_id in self.articles.keys():
                for article in self.articles[rss_feed_id]:
                    if article[6] == lang:
                        html += article[1].encode('utf-8') + \
                                """ - <a href="/description/%s:%s" rel="noreferrer" target="_blank">%s</a>
                                from <i><a href="%s">%s</a></i><br />\n""" % \
                                        (rss_feed_id, article[0].encode('utf-8'), article[2].encode('utf-8'), \
                                        self.feeds[rss_feed_id][5].encode('utf-8'), \
                                        self.feeds[rss_feed_id][3].encode('utf-8'))
        else:
            html += "Install the module "
            html += """<a href="http://pypi.python.org/pypi/oice.langdet/">oice.langdet</a>"""
        html += "<hr />\n"
        html += htmlfooter
        return html

    language.exposed = True


    def history(self, querystring="all"):
        """
        History
        """
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">\n"""

        if querystring == "all":
            html += "<h1>Chose a year</h1></br >\n"
        if "year" in querystring:
            the_year = querystring.split('-')[0].split(':')[1]
            if "month" not in querystring:
                html += "<h1>Chose a month for " + the_year + "</h1></br >\n"
        if "month" in querystring:
            the_month = querystring.split('-')[1].split(':')[1]
            html += "<h1>Articles of "+ calendar.month_name[int(the_month)] + \
                    ", "+ the_year +".</h1><br />\n"

        timeline = Counter()
        for rss_feed_id in self.feeds.keys():
            new_feed_section = True
            for article in self.articles[rss_feed_id]:

                if querystring == "all":
                    timeline[article[1].encode('utf-8').split(' ')[0].split('-')[0]] += 1

                elif querystring[:4] == "year":

                    if article[1].encode('utf-8').split(' ')[0].split('-')[0] == the_year:
                        timeline[article[1].encode('utf-8').split(' ')[0].split('-')[1]] += 1

                        if "month" in querystring:
                            if article[1].encode('utf-8').split(' ')[0].split('-')[1] == the_month:
                                if article[5] == "0":
                                    # not readed articles are in bold
                                    not_read_begin = "<b>"
                                    not_read_end = "</b>"
                                else:
                                    not_read_begin = ""
                                    not_read_end = ""

                                if article[7] == "1":
                                    like = """ <img src="/css/img/heart.png" title="I like this article!" />"""
                                else:
                                    like = ""

                                if new_feed_section is True:
                                    new_feed_section = False
                                    html += """<h2><a name="%s"><a href="%s" rel="noreferrer"
                                    target="_blank">%s</a></a>
                                    <a href="%s" rel="noreferrer"
                                    target="_blank"><img src="%s" width="28" height="28" /></a></h2>\n""" % \
                                        (rss_feed_id, \
                                        self.feeds[rss_feed_id][5].encode('utf-8'), \
                                        self.feeds[rss_feed_id][3].encode('utf-8'), \
                                        self.feeds[rss_feed_id][4].encode('utf-8'), \
                                        self.feeds[rss_feed_id][2].encode('utf-8'))

                                html += article[1].encode('utf-8') + \
                                        " - " + not_read_begin + \
                                        """<a href="/description/%s:%s" rel="noreferrer" target="_blank">%s</a>""" % \
                                                (rss_feed_id, article[0].encode('utf-8'), \
                                                utils.clear_string(article[2].encode('utf-8'))) + \
                                        not_read_end + like + \
                                        "<br />\n"

        if querystring == "all":
            query = "year"
        elif "year" in querystring:
            query = "year:" + the_year + "-month"
        if "month" not in querystring:
            html += '<div style="width: 35%; overflow:hidden; text-align: justify">' + \
                        utils.tag_cloud([(elem, timeline[elem]) for elem in timeline.keys()], \
                                            query) + '</div>'

        html += "<hr />\n"
        html += htmlfooter
        return html

    history.exposed = True


    def plain_text(self, target):
        """
        Display an article in plain text (without HTML tags).
        """
        try:
            feed_id, article_id = target.split(':')
        except:
            return self.error_page("This article do not exists.")
        try:
            articles_list = self.articles[feed_id]
        except KeyError:
            return self.error_page("This feed do not exists.")
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        feed_id, article_id = target.split(':')
        for article in articles_list:
            if article_id == article[0]:
                html += """<h1><i>%s</i> from <a href="/all_articles/%s">%s</a></h1>\n<br />\n"""% \
                                    (article[2].encode('utf-8'), feed_id, \
                                    self.feeds[feed_id][3].encode('utf-8'))
                description = utils.clear_string(article[4].encode('utf-8'))
                if description:
                    html += description
                else:
                    html += "No description available."
        html += "\n<hr />\n" + htmlfooter
        return html

    plain_text.exposed = True


    def error_page(self, message):
        """
        Display a message (bad feed id, bad article id, etc.)
        """
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        html += """%s""" % message
        html += "\n<hr />\n" + htmlfooter
        return html

    error_page.exposed = True


    def mark_as_read(self, target):
        """
        Mark one (or more) article(s) as read by setting the value of the field
        'article_readed' of the SQLite database to 1.
        """
        param, _, identifiant = target.partition(':')
        try:
            LOCKER.acquire()
            conn = sqlite3.connect(utils.sqlite_base, isolation_level = None)
            c = conn.cursor()
            # Mark all articles as read.
            if param == "All":
                c.execute("UPDATE articles SET article_readed=1 WHERE article_readed='0'")
            # Mark all articles from a feed as read.
            elif param == "Feed" or param == "Feed_FromMainPage":
                c.execute("UPDATE articles SET article_readed=1 WHERE article_readed='0' AND feed_link='" + \
                            self.feeds[identifiant][4].encode('utf-8') + "'")
            # Mark an article as read.
            elif param == "Article":
                c.execute("UPDATE articles SET article_readed=1 WHERE article_link='" + \
                            identifiant + "'")
            conn.commit()
            c.close()
        except Exception:
            self.error_page("Impossible to mark this article as read (database error).")
        finally:
            LOCKER.release()

        if param == "All" or param == "Feed_FromMainPage":
            return self.index()
        elif param == "Feed":
            return self.all_articles(identifiant)

    mark_as_read.exposed = True


    def list_notification(self):
        """
        List all active e-mail notifications.
        """
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        html += "<h1>You are receiving e-mails for the following feeds:</h1>\n"
        for rss_feed_id in self.feeds.keys():
            if self.feeds[rss_feed_id][6] == "1":
                html += """\t<a href="/all_articles/%s">%s</a> - <a href="/mail_notification/stop:%s">Stop</a><br />\n""" % \
                        (rss_feed_id, self.feeds[rss_feed_id][3].encode('utf-8'), rss_feed_id)

        html += """<p>Notifications are sent to: <a href="mail:%s">%s</a></p>""" % \
                        (utils.mail_to, utils.mail_to)
        html += "\n<hr />\n" + htmlfooter
        return html

    list_notification.exposed = True


    def mail_notification(self, param):
        """
        Enable or disable to notifications of news for a feed.
        """
        try:
            action, feed_id = param.split(':')
        except:
            return self.error_page("Bad URL")
        if feed_id not in self.feeds.keys():
            return self.error_page("This feed do not exists.")
        conn = sqlite3.connect(utils.sqlite_base, isolation_level = None)
        c = conn.cursor()
        if action == "start":
            try:
                c.execute("UPDATE feeds SET mail=1 WHERE feed_site_link='" +
                            self.feeds[feed_id][5].encode('utf-8') + "'")
            except:
                return self.error_page("Error")
        else:
            try:
                c.execute("UPDATE feeds SET mail=0 WHERE feed_site_link='" +
                            self.feeds[feed_id][5].encode('utf-8') + "'")
            except:
                return self.error_page("Error")
        conn.commit()
        c.close()
        return self.index()

    mail_notification.exposed = True


    def like(self, param):
        """
        Mark or unmark an article as favorites.
        """
        try:
            action, feed_id, article_id = param.split(':')
        except:
            return self.error_page("Bad URL")
        try:
            articles_list = self.articles[feed_id]
        except KeyError:
            return self.error_page("This feed do not exists.")
        for article in articles_list:
            if article_id == article[0]:
                try:
                    conn = sqlite3.connect(utils.sqlite_base, isolation_level = None)
                    c = conn.cursor()
                    # Mark all articles as read.
                    if action == "yes":
                        c.execute("UPDATE articles SET like=1 WHERE article_link='" + \
                                    article[3] + "'")
                    if action == "no":
                        c.execute("UPDATE articles SET like=0 WHERE article_link='" + \
                                    article[3] + "'")
                    conn.commit()
                    c.close()
                except Exception:
                    self.error_page("Impossible to like/dislike this article (database error).")
                break
        return self.description(feed_id+":"+article_id)

    like.exposed = True


    def list_favorites(self):
        """
        List of favorites articles
        """
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        html += "<h1>Your favorites articles</h1>"
        for rss_feed_id in self.feeds.keys():
            new_feed_section = True
            for article in self.articles[rss_feed_id]:
                if article[7] == "1":
                    if new_feed_section is True:
                        new_feed_section = False
                        html += """<h2><a name="%s"><a href="%s" rel="noreferrer"
                        target="_blank">%s</a></a>
                        <a href="%s" rel="noreferrer"
                        target="_blank"><img src="%s" width="28" height="28" /></a></h2>\n""" % \
                            (rss_feed_id, \
                            self.feeds[rss_feed_id][5].encode('utf-8'), \
                            self.feeds[rss_feed_id][3].encode('utf-8'), \
                            self.feeds[rss_feed_id][4].encode('utf-8'), \
                            self.feeds[rss_feed_id][2].encode('utf-8'))

                    html += article[1].encode('utf-8') + \
                            """ - <a href="/description/%s:%s" rel="noreferrer" target="_blank">%s</a><br />\n""" % \
                                    (rss_feed_id, article[0].encode('utf-8'), article[2].encode('utf-8'))
        html += "<hr />\n"
        html += htmlfooter
        return html

    list_favorites.exposed = True


    def add_feed(self, url):
        """
        Add a new feed with the URL of a page.
        """
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        # search the feed in the HTML page with BeautifulSoup
        feed_url = utils.search_feed(url)
        if feed_url is None:
            return self.error_page("Impossible to find a feed at this URL.")
        # if a feed exists
        else:
            result = utils.add_feed(feed_url)
        # if the feed is not already in the file feed.lst
        if result is False:
            html +=  "<p>You are already following this feed!</p>"
        else:
            html += """<p>Feed added. You can now <a href="/fetch/">fetch your feeds</a>.</p>"""
        html += "<br />"
        html += """<a href="/management/">Back to the management page.</a><br />\n"""
        html += "<hr />\n"
        html += htmlfooter
        return html

    add_feed.exposed = True


    def remove_feed(self, feed_id):
        """
        Remove a feed from the file feed.lst and from the SQLite base.
        """
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        if feed_id in self.feeds.keys():
            utils.remove_feed(self.feeds[feed_id][4])
            html += """<p>All articles from the feed <i>%s</i> are now removed from the base.</p><br />""" % \
                (self.feeds[feed_id][3].encode('utf-8'),)
        else:
            return self.error_page("This feed do not exists.")
        html += """<a href="/management/">Back to the management page.</a><br />\n"""
        html += "<hr />\n"
        html += htmlfooter
        return html

    remove_feed.exposed = True


    def delete_article(self, param):
        """
        Delete an article.
        """
        try:
            feed_id, article_id = param.split(':')
            articles_list = self.articles[feed_id]
        except:
            return self.error_page("This article do not exists.")
        for article in articles_list:
            if article_id == article[0]:
                try:
                    conn = sqlite3.connect(utils.sqlite_base, isolation_level = None)
                    c = conn.cursor()
                    c.execute("DELETE FROM articles WHERE article_link='" + article[3] +"'")
                    conn.commit()
                    c.close()
                except Exception, e:
                    return e
        return self.index()

    delete_article.exposed = True


    def drop_base(self):
        """
        Delete all articles
        """
        utils.drop_base()
        return self.management()

    drop_base.exposed = True


    def export(self, export_method):
        """
        Export articles stored in the SQLite database in text
        (raw or HTML) files.
        """
        for rss_feed_id in self.feeds.keys():
            folder = utils.path + "/var/export/" + \
                        utils.normalize_filename(self.feeds[rss_feed_id][3].strip().encode("utf-8"))
            try:
                os.makedirs(folder)
            except OSError:
                return self.error_page(utils.path + "var/export/"+" already exists.\nYou should delete this folder.")

            for article in self.articles[rss_feed_id]:
                try:
                    name = article[1].strip().replace(' ', '_')

                    # Export all articles in HTML format
                    if export_method == "export_HTML":
                        name = os.path.normpath(folder + "/" + name + ".html")
                        f = open(name, "w")
                        content = htmlheader()
                        content += '\n<div style="width: 50%; overflow:hidden; text-align: justify; margin:0 auto">\n'
                        content += """<h1><a href="%s">%s</a></h1><br />""" % \
                                    (article[3].encode('utf-8'), article[2].encode('utf-8'))
                        content += article[4].encode('utf-8')
                        content += "</div>\n<hr />\n"
                        content += htmlfooter
                    # Export all articles in raw text
                    elif export_method == "export_TXT":
                        name = os.path.normpath(folder + "/" + name + ".txt")
                        f = open(name, "w")
                        content = "Title: " + article[2].encode('utf-8') + "\n\n\n"
                        content += utils.clear_string(article[4].encode('utf-8'))

                    f.write(content)
                except IOError:
                    pass
                finally:
                    f.close()
        return self.management()

    export.exposed = True


    def update(self, path=None, event = None):
        """
        Synchronizes transient objects (dictionary of feed and articles)
        with the database.
        Called when a changes in the database is detected.
        """
        self.articles, self.feeds = utils.load_feed()
        self.nb_articles = sum([feed[0] for feed in self.feeds.values()])
        self.nb_unread_articles = sum([feed[1] for feed in self.feeds.values()])
        self.nb_mail_notifications = len([feed for feed in self.feeds.values() \
                                if feed[6] == "1"])
        self.nb_favorites = sum([len([article for article in self.articles[feed_id] \
                                if article[7] == "1"]) \
                                    for feed_id in self.feeds.keys()])
        if self.articles != {}:
            print "Base (%s) loaded" % utils.sqlite_base
        else:
            print "Base (%s) empty!" % utils.sqlite_base

    def watch_base(self):
        """Monitor a file.

        Detect the changes in base of feeds.
        When a change is detected, reload the base.
        """
        mon = gamin.WatchMonitor()
        time.sleep(10)
        mon.watch_file(utils.sqlite_base, self.update)
        ret = mon.event_pending()
        try:
            print "Watching %s" % utils.sqlite_base
            while True:
                ret = mon.event_pending()
                if ret > 0:
                    print "The base of feeds (%s) has changed.\nReloading..." % utils.sqlite_base
                    ret = mon.handle_one_event()
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        print "Stop watching", sqlite_base
        mon.stop_watch(sqlite_base)
        del mon

    def watch_base_classic(self):
        """
        Monitor the base of feeds if the module gamin is not
        installed.
        """
        time.sleep(10)
        old_time = 0
        try:
            print "Watching %s" % utils.sqlite_base
            while True:
                time.sleep(1)
                # simple test (date of last modification: getmtime)
                if os.path.getmtime(utils.sqlite_base) != old_time:
                    print "The base of feeds (%s) has changed.\nReloading..." % utils.sqlite_base
                    self.update()
                    old_time = os.path.getmtime(utils.sqlite_base)
        except KeyboardInterrupt:
            pass
        print "Stop watching", utils.sqlite_base


if __name__ == '__main__':
    # Point of entry in execution mode
    print "Launching pyAggr3g470r..."
    LOCKER = threading.Lock()
    root = Root()
    if not os.path.isfile(utils.sqlite_base):
        # create the SQLite base if not exists
        print "Creating data base..."
        utils.create_base()
    # load the informations from base in memory
    print "Loading informations from data base..."
    root.update()
    # launch the available base monitoring method (gamin or classic)
    try:
        import gamin
        thread_watch_base = threading.Thread(None, root.watch_base, None, ())
    except:
        print "The gamin module is not installed."
        print "The base of feeds will be monitored with the simple method."
        thread_watch_base = threading.Thread(None, root.watch_base_classic, None, ())
    thread_watch_base.setDaemon(True)
    thread_watch_base.start()
    cherrypy.quickstart(root, config=path)

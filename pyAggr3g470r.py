#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2012  Cédric Bonhomme - http://cedricbonhomme.org/
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
__version__ = "$Revision: 3.1 $"
__date__ = "$Date: 2010/01/29 $"
__revision__ = "$Date: 2012/03/09 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

#
# This file contains the "Root" class which describes
# all pages of pyAggr3g470r. These pages are:
# - main page;
# - management;
# - history;
# - favorites;
# - notifications;
# - unread;
# - feed summary.
#

import os
import re
import time
import cherrypy
import calendar

from collections import Counter
import datetime

import utils
import export
import mongodb
import feedgetter
from qrcode.pyqrnative.PyQRNative import QRCode, QRErrorCorrectLevel, CodeOverflowException
from qrcode import qr


def error_page_404(status, message, traceback, version):
    """
    Display an error if the page does not exist.
    """
    html = htmlheader()
    html += htmlnav
    html += "<br /><br />Error %s - This page does not exist." % status
    html += "\n<hr />\n" + htmlfooter
    return html

def handle_error():
    """
    Handle different type of errors.
    """
    html = htmlheader()
    html += htmlnav
    html += "<br /><br />Sorry, an error occured"
    html += "\n<hr />\n" + htmlfooter
    cherrypy.response.status = 500
    cherrypy.response.body = [html]

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
        '\n\t<script type="text/javascript" src="https://apis.google.com/js/plusone.js"></script>\n' + \
        '</head>\n'

htmlfooter = '<p>This software is under GPLv3 license. You are welcome to copy, modify or' + \
            ' redistribute the source code according to the' + \
            ' <a href="http://www.gnu.org/licenses/gpl-3.0.txt">GPLv3</a> license.</p></div>\n' + \
            '</body>\n</html>'

htmlnav = '<body>\n<h1><div class="right innerlogo"><a href="/"><img src="/img/tuxrss.png"' + \
        """ title="What's new today?"/></a>""" + \
        '</div><a name="top"><a href="/">pyAggr3g470r - News aggregator</a></a></h1>\n<a' + \
        ' href="http://bitbucket.org/cedricbonhomme/pyaggr3g470r/" rel="noreferrer" target="_blank">' + \
        'pyAggr3g470r (source code)</a>'


class Root:
    """
    Root class.
    All pages of pyAggr3g470r are described in this class.
    """
    def __init__(self):
        """
        """
        self.mongo = mongodb.Articles(utils.MONGODB_ADDRESS, utils.MONGODB_PORT)

    def index(self):
        """
        Main page containing the list of feeds and articles.
        """
        feeds = self.mongo.get_all_collections()
        nb_unread_articles = self.mongo.nb_unread_articles()
        nb_favorites = self.mongo.nb_favorites()
        nb_mail_notifications = self.mongo.nb_mail_notifications()

        # if there are unread articles, display the number in the tab of the browser
        html = htmlheader((nb_unread_articles and \
                            ['(' + str(nb_unread_articles) +') '] or \
                            [""])[0])
        html += htmlnav
        html += self.create_right_menu()
        html += """<div class="left inner">\n"""

        if feeds:
            html += '<a href="/management/"><img src="/img/management.png" title="Management" /></a>\n'
            html += '<a href="/history/"><img src="/img/history.png" title="History" /></a>\n'
            html += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\n'

            html += """<a href="/favorites/"><img src="/img/heart-32x32.png" title="Your favorites (%s)" /></a>\n""" % \
                (nb_favorites,)

            html += """<a href="/notifications/"><img src="/img/email-follow.png" title="Active e-mail notifications (%s)" /></a>\n""" % \
                (nb_mail_notifications,)

            html += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
            if nb_unread_articles != 0:
                html += '<a href="/mark_as_read/"><img src="/img/mark-as-read.png" title="Mark articles as read" /></a>\n'
                html += """<a href="/unread/"><img src="/img/unread.png" title="Unread article(s): %s" /></a>\n""" % \
                    (nb_unread_articles,)
        html += '<a accesskey="F" href="/fetch/"><img src="/img/check-news.png" title="Check for news" /></a>\n'


        # The main page display all the feeds.
        for feed in feeds:
            html += """<h2><a name="%s"><a href="%s" rel="noreferrer"
                    target="_blank">%s</a></a>
                    <a href="%s" rel="noreferrer"
                    target="_blank"><img src="%s" width="28" height="28" /></a></h2>\n""" % \
                        (feed["feed_id"], feed["feed_link"], feed["feed_title"], \
                        feed["feed_link"], feed["feed_image"])

            # The main page display only 10 articles by feeds.
            for article in self.mongo.get_articles_from_collection(feed["feed_id"])[:10]:
                if article["article_readed"] == False:
                    # not readed articles are in bold
                    not_read_begin, not_read_end = "<b>", "</b>"
                else:
                    not_read_begin, not_read_end = "", ""

                # display a heart for faved articles
                if article["article_like"] == True:
                    like = """ <img src="/img/heart.png" title="I like this article!" />"""
                else:
                    like = ""

                # Descrition for the CSS ToolTips
                article_content = utils.clear_string(article["article_content"])
                if article_content:
                    description = " ".join(article_content.split(' ')[:55])
                else:
                    description = "No description."
                # Title of the article
                article_title = article["article_title"]
                if len(article_title) >= 110:
                    article_title = article_title[:110] + " ..."

                # a description line per article (date, title of the article and
                # CSS description tooltips on mouse over)
                html += str(article["article_date"]) + " - " + \
                        """<a class="tooltip" href="/article/%s:%s" rel="noreferrer" target="_blank">%s%s%s<span class="classic">%s</span></a>""" % \
                                (feed["feed_id"], article["article_id"], not_read_begin, \
                                article_title, not_read_end, description) + like + "<br />\n"
            html += "<br />\n"

            # some options for the current feed
            html += """<a href="/articles/%s">All articles</a>&nbsp;&nbsp;&nbsp;""" % (feed["feed_id"],)
            html += """<a href="/feed/%s">Feed summary</a>&nbsp;&nbsp;&nbsp;""" % (feed["feed_id"],)
            if self.mongo.nb_unread_articles(feed["feed_id"]) != 0:
                html += """&nbsp;&nbsp;<a href="/mark_as_read/Feed_FromMainPage:%s">Mark all as read</a>""" % (feed["feed_id"],)
                html += """&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="/unread/%s" title="Unread article(s)">Unread article(s) (%s)</a>""" % (feed["feed_id"], self.mongo.nb_unread_articles(feed["feed_id"]))
            if feed["mail"] == "0":
                html += """<br />\n<a href="/mail_notification/1:%s" title="By e-mail">Stay tuned</a>""" % (feed["feed_id"],)
            else:
                html += """<br />\n<a href="/mail_notification/0:%s" title="By e-mail">Stop staying tuned</a>""" %  (feed["feed_id"],)
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
        html += """<form method=get action="/q/"><input type="search" name="querystring" value="" placeholder="Search articles" maxlength=2048 autocomplete="on"></form>\n"""
        html += "<hr />\n"
        # insert the list of feeds in the menu
        html += self.create_list_of_feeds()
        html += "</div>\n"

        return html

    def create_list_of_feeds(self):
        """
        Create the list of feeds.
        """
        feeds = self.mongo.get_all_collections()
        html = """<div class="nav_container">Your feeds (%s):<br />\n""" % len(feeds)
        for feed in feeds:
            if self.mongo.nb_unread_articles(feed["feed_id"]) != 0:
                # not readed articles are in bold
                not_read_begin, not_read_end = "<b>", "</b>"
            else:
                not_read_begin, not_read_end = "", ""
            html += """<div><a href="/#%s">%s</a> (<a href="/unread/%s" title="Unread article(s)">%s%s%s</a> / %s)</div>""" % \
                            (feed["feed_id"], feed["feed_title"], feed["feed_id"], not_read_begin, \
                            self.mongo.nb_unread_articles(feed["feed_id"]), not_read_end, self.mongo.nb_articles(feed["feed_id"]))
        return html + "</div>"


    def management(self, max_nb_articles=5):
        """
        Management page.
        Allows adding and deleting feeds. Export functions of the MongoDB data base
        and display some statistics.
        """
        feeds = self.mongo.get_all_collections()
        nb_mail_notifications = self.mongo.nb_mail_notifications()
        nb_favorites = self.mongo.nb_favorites()
        nb_articles = self.mongo.nb_articles()
        nb_unread_articles = self.mongo.nb_unread_articles()
        
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">\n"""
        html += "<h1>Add Feeds</h1>\n"
        # Form: add a feed
        html += """<form method=get action="/add_feed/"><input type="url" name="url" placeholder="URL of a site" maxlength=2048 autocomplete="off">\n<input type="submit" value="OK"></form>\n"""

        if feeds:
            # Form: delete a feed
            html += "<h1>Delete Feeds</h1>\n"
            html += """<form method=get action="/remove_feed/"><select name="feed_id">\n"""
            for feed in feeds:
                html += """\t<option value="%s">%s</option>\n""" % (feed["feed_id"], feed["feed_title"])
            html += """</select><input type="submit" value="OK"></form>\n"""

            html += """<p>Active e-mail notifications: <a href="/notifications/">%s</a></p>\n""" % \
                        (nb_mail_notifications,)
            html += """<p>You like <a href="/favorites/">%s</a> article(s).</p>\n""" % \
                        (nb_favorites, )

        html += "<hr />\n"

        # Informations about the data base of articles
        html += """<p>%s article(s) are loaded from the database with
                <a href="/unread/">%s unread article(s)</a>.<br />\n""" % \
                    (nb_articles, nb_unread_articles)
        #html += """Database: %s.\n<br />Size: %s bytes.<br />\n""" % \
                    #(os.path.abspath(utils.sqlite_base), os.path.getsize(utils.sqlite_base))
        html += '<a href="/statistics/">Advanced statistics.</a></p>\n'

        html += """<form method=get action="/fetch/">\n<input type="submit" value="Fetch all feeds"></form>\n"""
        html += """<form method=get action="/drop_base">\n<input type="submit" value="Delete all articles"></form>\n"""


        html += '<form method=get action="/set_max_articles/">\n'
        html += "For each feed only load the "
        html += """<input type="number" name="max_nb_articles" value="%s" min="1" step="1" size="2">\n""" % (max_nb_articles)
        html += " last articles."
        if utils.MAX_NB_ARTICLES == -1:
            html += "<br />All articles are currently loaded.\n"
        else:
            html += "<br />For each feed only " + str(utils.MAX_NB_ARTICLES) + " articles are currently loaded. "
            html += '<a href="/set_max_articles/-1">Load all articles.</a><br />\n'
        html += "</form>\n"

        # Export functions
        html += "<h1>Export articles</h1>\n\n"
        html += """<form method=get action="/export/"><select name="export_method">\n"""
        html += """\t<option value="export_html" selected='selected'>HTML (simple Webzine)</option>\n"""
        html += """\t<option value="export_epub">ePub</option>\n"""
        html += """\t<option value="export_pdf">PDF</option>\n"""
        html += """\t<option value="export_txt">Text</option>\n"""
        html += """</select>\n\t<input type="submit" value="Export">\n</form>\n"""
        html += "<hr />"
        html += htmlfooter
        return html

    management.exposed = True


    def statistics(self, word_size=6):
        """
        More advanced statistics.
        """
        articles = self.mongo.get_all_articles()
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">\n"""

        # Some statistics (most frequent word)
        if articles:
            top_words = utils.top_words(articles, n=50, size=int(word_size))
            html += "<h1>Statistics</h1>\n<br />\n"
            # Tags cloud
            html += 'Minimum size of a word:'
            html += '<form method=get action="/statistics/">'
            html += """<input type="number" name="word_size" value="%s" min="2" max="15" step="1" size="2">""" % (word_size)
            html += '<input type="submit" value="OK"></form>\n'
            html += '<br /><h3>Tag cloud</h3>\n'
            html += '<div style="width: 35%; overflow:hidden; text-align: justify">' + \
                        utils.tag_cloud(top_words) + '</div>'
            html += "<hr />\n"

        html += htmlfooter
        return html

    statistics.exposed = True


    def q(self, querystring=None):
        """
        Simply search for the string 'querystring'
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
            for article in self.feeds[feed_id].articles.values():
                article_content = utils.clear_string(article.article_description)
                if not article_content:
                    utils.clear_string(article.article_title)
                if wordre.findall(article_content) != []:
                    if article.article_readed == "0":
                        # not readed articles are in bold
                        not_read_begin, not_read_end = "<b>", "</b>"
                    else:
                        not_read_begin, not_read_end = "", ""

                    html += article.article_date + " - " + not_read_begin + \
                            """<a href="/article/%s:%s" rel="noreferrer" target="_blank">%s</a>""" % \
                                    (feed_id, article.article_id, article.article_title) + \
                            not_read_end + """<br />\n"""
        else:
            articles = self.mongo.get_all_articles()
            for feed in self.feeds.values():
                new_feed_section = True
                for article in articles:
                    article_content = utils.clear_string(article.article_description)
                    if not article_content:
                        utils.clear_string(article.article_title)
                    if wordre.findall(article_content) != []:
                        if new_feed_section is True:
                            new_feed_section = False
                            html += """<h2><a href="/articles/%s" rel="noreferrer" target="_blank">%s</a><a href="%s" rel="noreferrer" target="_blank"><img src="%s" width="28" height="28" /></a></h2>\n""" % \
                                (feed.feed_id, feed.feed_title, feed.feed_link, feed.feed_image)

                        if article.article_readed == "0":
                            # not readed articles are in bold
                            not_read_begin, not_read_end = "<b>", "</b>"
                        else:
                            not_read_begin, not_read_end = "", ""

                        # display a heart for faved articles
                        if article.like == "1":
                            like = """ <img src="/img/heart.png" title="I like this article!" />"""
                        else:
                            like = ""

                        # descrition for the CSS ToolTips
                        article_content = utils.clear_string(article.article_description)
                        if article_content:
                            description = " ".join(article_content[:500].split(' ')[:-1])
                        else:
                            description = "No description."

                        # a description line per article (date, title of the article and
                        # CSS description tooltips on mouse over)
                        html += article.article_date + " - " + \
                                """<a class="tooltip" href="/article/%s:%s" rel="noreferrer" target="_blank">%s%s%s<span class="classic">%s</span></a>""" % \
                                        (feed.feed_id, article.article_id, not_read_begin, \
                                        article.article_title[:150], not_read_end, description) + like + "<br />\n"
        html += "<hr />"
        html += htmlfooter
        return html

    q.exposed = True


    def fetch(self):
        """
        Fetch all feeds.
        """
        feed_getter = feedgetter.FeedGetter()
        feed_getter.retrieve_feed()
        return self.index()

    fetch.exposed = True


    def article(self, param):
        """
        Display the article in parameter in a new Web page.
        """
        try:
            feed_id, article_id = param.split(':')
            feed = self.mongo.get_collection(feed_id)
            articles = self.mongo.get_articles_from_collection(feed_id)
            article = self.mongo.get_article(feed_id, article_id)
        except:
            return self.error_page("Bad URL. This article do not exists.")
        html = htmlheader()
        html += htmlnav
        html += """<div>"""

        if article["article_readed"] == False:
            # if the current article is not yet readed, update the database
            self.mark_as_read("Article:"+article["article_id"]+":"+feed["feed_id"])

        html += '\n<div style="width: 50%; overflow:hidden; text-align: justify; margin:0 auto">\n'
        # Title of the article
        html += """<h1><i>%s</i> from <a href="/feed/%s">%s</a></h1>\n<br />\n""" % \
                        (article["article_title"], feed_id, feed["feed_title"])
        if article["article_like"] == True:
            html += """<a href="/like/0:%s:%s"><img src="/img/heart.png" title="I like this article!" /></a>""" % \
                        (feed_id, article["article_id"])
        else:
            html += """<a href="/like/1:%s:%s"><img src="/img/heart_open.png" title="Click if you like this article." /></a>""" % \
                        (feed_id, article["article_id"])
        html += """&nbsp;&nbsp;<a href="/delete_article/%s:%s"><img src="/img/cross.png" title="Delete this article" /></a>""" % \
                        (feed_id, article["article_id"])
        html += "<br /><br />"

        # Description (full content) of the article
        description = article["article_content"]
        if description:
            p = re.compile(r'<code><')
            q = re.compile(r'></code>')

            description = p.sub('<code>&lt;', description)
            description = q.sub('&gt;</code>', description)

            html += description + "\n<br /><br /><br />"
        else:
            html += "No description available.\n<br /><br /><br />"

        # Generation of the QR Code for the current article
        try:
            os.makedirs("./var/qrcode/")
        except OSError:
            pass
        if not os.path.isfile("./var/qrcode/" + article_id + ".png"):
            # QR Code generation
            try:
                if len(utils.clear_string(description)) > 4296:
                    raise Exception()
                f = qr.QRUrl(url = utils.clear_string(description))
                f.make()
            except:
                f = qr.QRUrl(url = article["article_link"])
                f.make()
            f.save("./var/qrcode/"+article_id+".png")

        # Previous and following articles
        articles_list = articles.distinct("article_id")
        try:
            following = articles[articles_list.index(article_id) - 1]
            html += """<div style="float:right;"><a href="/article/%s:%s" title="%s"><img src="/img/following-article.png" /></a></div>\n""" % \
                (feed_id, following["article_id"], following["article_title"])
        except Exception, e:
            print e
        try:
            previous = articles[articles_list.index(article_id) + 1]
        except:
            previous = articles[0]
        finally:
            html += """<div style="float:left;"><a href="/article/%s:%s" title="%s"><img src="/img/previous-article.png" /></a></div>\n""" % \
                (feed_id, previous["article_id"], previous["article_title"])

        html += "\n</div>\n"

        # Footer menu
        html += "<hr />\n"
        html += """\n<a href="/plain_text/%s:%s">Plain text</a>\n""" % (feed_id, article["article_id"])
        html += """ - <a href="/epub/%s:%s">Export to EPUB</a>\n""" % (feed_id, article["article_id"])
        html += """<br />\n<a href="%s">Complete story</a>\n<br />\n""" % (article["article_link"],)

        # Share this article:
        html += "Share this article:<br />\n"
        # on Diaspora
        html += """<a href="javascript:(function(){f='https://%s/bookmarklet?url=%s&amp;title=%s&amp;notes=%s&amp;v=1&amp;';a=function(){if(!window.open(f+'noui=1&amp;jump=doclose','diasporav1','location=yes,links=no,scrollbars=no,toolbar=no,width=620,height=250'))location.href=f+'jump=yes'};if(/Firefox/.test(navigator.userAgent)){setTimeout(a,0)}else{a()}})()">\n\t
                <img src="/img/diaspora.png" title="Share on Diaspora" /></a>\n""" % \
                        (utils.DIASPORA_POD, article["article_link"], article["article_title"], "via pyAggr3g470r")

        # on Identi.ca
        html += """\n\n<a href="http://identi.ca/index.php?action=newnotice&status_textarea=%s: %s" title="Share on Identi.ca" target="_blank"><img src="/img/identica.png" /></a>""" % \
                        (article["article_title"], article["article_link"])

        # on Pinboard
        html += """\n\n\t<a href="https://api.pinboard.in/v1/posts/add?url=%s&description=%s"
                rel="noreferrer" target="_blank">\n
                <img src="/img/pinboard.png" title="Share on Pinboard" /></a>""" % \
                        (article["article_link"], article["article_title"])

        # on Digg
        html += """\n\n\t<a href="http://digg.com/submit?url=%s&title=%s"
                rel="noreferrer" target="_blank">\n
                <img src="/img/digg.png" title="Share on Digg" /></a>""" % \
                        (article["article_link"], article["article_title"])
        # on reddit
        html += """\n\n\t<a href="http://reddit.com/submit?url=%s&title=%s"
                rel="noreferrer" target="_blank">\n
                <img src="/img/reddit.png" title="Share on reddit" /></a>""" % \
                        (article["article_link"], article["article_title"])
        # on Scoopeo
        html += """\n\n\t<a href="http://scoopeo.com/scoop/new?newurl=%s&title=%s"
                rel="noreferrer" target="_blank">\n
                <img src="/img/scoopeo.png" title="Share on Scoopeo" /></a>""" % \
                        (article["article_link"], article["article_title"])
        # on Blogmarks
        html += """\n\n\t<a href="http://blogmarks.net/my/new.php?url=%s&title=%s"
                rel="noreferrer" target="_blank">\n
                <img src="/img/blogmarks.png" title="Share on Blogmarks" /></a>""" % \
                        (article["article_link"], article["article_title"])

        # Google +1 button
        html += """\n\n<g:plusone size="standard" count="true" href="%s"></g:plusone>""" % \
                        (article["article_link"],)


        # QRCode (for smartphone)
        html += """<br />\n<a href="/var/qrcode/%s.png"><img src="/var/qrcode/%s.png" title="Share with your smartphone" width="500" height="500" /></a>""" % (article_id, article_id)
        html += "<hr />\n" + htmlfooter
        return html

    article.exposed = True


    def feed(self, feed_id, word_size=6):
        """
        This page gives summary informations about a feed (number of articles,
        unread articles, average activity, tag cloud, e-mail notification and
        favourite articles for the current feed.
        """
        try:
            feed = self.mongo.get_collection(feed_id)
            articles = self.mongo.get_articles_from_collection(feed_id)
        except KeyError:
            return self.error_page("This feed do not exists.")
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        html += "<p>The feed <b>" + feed["feed_title"] + "</b> contains <b>" + str(self.mongo.nb_articles(feed_id)) + "</b> articles. "
        html += "Representing " + str((round(float(self.mongo.nb_articles(feed_id)) / 1000, 4)) * 100) + " % of the total " #hack
        html += "(" + str(1000) + ").</p>"
        if articles != []:
            html += "<p>" + (self.mongo.nb_unread_articles(feed_id) == 0 and ["All articles are read"] or [str(self.mongo.nb_unread_articles(feed_id)) + \
                    " unread article" + (self.mongo.nb_unread_articles(feed_id) == 1 and [""] or ["s"])[0]])[0] + ".</p>"
        if feed["mail"] == True:
                html += """<p>You are receiving articles from this feed to the address: <a href="mail:%s">%s</a>. """ % \
                        (utils.mail_to, utils.mail_to)
                html += """<a href="/mail_notification/0:%s">Stop</a> receiving articles from this feed.</p>""" % \
                        (feed[feed_id], )

        if articles != []:
            last_article = utils.string_to_datetime(str(articles[0]["article_date"]))
            first_article = utils.string_to_datetime(str(articles[self.mongo.nb_articles(feed_id)-2]["article_date"]))
            delta = last_article - first_article
            delta_today = datetime.datetime.fromordinal(datetime.date.today().toordinal()) - last_article
            html += "<p>The last article was posted " + str(abs(delta_today.days))  + " day(s) ago.</p>"
            if delta.days > 0:
                html += """<p>Daily average: %s,""" % (str(round(float(self.mongo.nb_articles(feed_id))/abs(delta.days), 2)),)
                html += """ between the %s and the %s.</p>\n""" % \
	              (str(articles[self.mongo.nb_articles(feed_id)-2]["article_date"])[:10], str(articles[0]["article_date"])[:10])

        html += "<br /><h1>Recent articles</h1>"
        for article in articles[:10]:
            if article["article_readed"] == False:
                # not readed articles are in bold
                not_read_begin, not_read_end = "<b>", "</b>"
            else:
                not_read_begin, not_read_end = "", ""

            # display a heart for faved articles
            if article["article_like"] == True:
                like = """ <img src="/img/heart.png" title="I like this article!" />"""
            else:
                like = ""

            # Descrition for the CSS ToolTips
            article_content = utils.clear_string(article["article_content"])
            if article_content:
                description = " ".join(article_content[:500].split(' ')[:-1])
            else:
                description = "No description."
            # Title of the article
            article_title = article["article_title"]
            if len(article_title) >= 110:
                article_title = article_title[:110] + " ..."

            # a description line per article (date, title of the article and
            # CSS description tooltips on mouse over)
            html += str(article["article_date"]) + " - " + \
                    """<a class="tooltip" href="/article/%s:%s" rel="noreferrer" target="_blank">%s%s%s<span class="classic">%s</span></a>""" % \
                            (feed["feed_id"], article["article_id"], not_read_begin, \
                            article_title, not_read_end, description) + like + "<br />\n"
        html += "<br />\n"
        html += """<a href="/articles/%s">All articles</a>&nbsp;&nbsp;&nbsp;""" % (feed["feed_id"],)

        favs = [article for article in articles if article["article_like"] == True]
        if len(favs) != 0:
            html += "<br /></br /><h1>Your favorites articles for this feed</h1>"
            for article in favs:
                if article["like"] == True:
                    # descrition for the CSS ToolTips
                    article_content = utils.clear_string(article["article_content"])
                    if article_content:
                        description = " ".join(article_content[:500].split(' ')[:-1])
                    else:
                        description = "No description."

                    # a description line per article (date, title of the article and
                    # CSS description tooltips on mouse over)
                    html += str(article["article_date"]) + " - " + \
                            """<a class="tooltip" href="/article/%s:%s" rel="noreferrer" target="_blank">%s<span class="classic">%s</span></a><br />\n""" % \
                                    (feed["feed_id"], article["article_id"], article["article_title"][:150], description)


        # This section enables the user to edit informations about
        # the current feed:
        #  - feed logo;
        #  - feed name;
        #  - URL of the feed (not the site);
        html += "<br />\n<h1>Edit this feed</h1>\n"
        html += '\n\n<form method=post action="/change_feed_name/">' + \
                '<input type="text" name="new_feed_name" value="" ' + \
                'placeholder="Enter a new name (then press Enter)." maxlength=2048 autocomplete="on" size="50" />' + \
                """<input type="hidden" name="feed_url" value="%s" /></form>\n""" % \
                    (feed["feed_link"],)
        html += '\n\n<form method=post action="/change_feed_url/">' + \
                '<input type="url" name="new_feed_url" value="" ' + \
                'placeholder="Enter a new URL in order to retrieve articles (then press Enter)." maxlength=2048 autocomplete="on" size="50" />' + \
                """<input type="hidden" name="old_feed_url" value="%s" /></form>\n""" % \
                    (feed["feed_link"],)
        html += '\n\n<form method=post action="/change_feed_logo/">' + \
                '<input type="url" name="new_feed_logo" value="" ' + \
                'placeholder="Enter the URL of the logo (then press Enter)." maxlength=2048 autocomplete="on" size="50" />' + \
                """<input type="hidden" name="feed_url" value="%s" /></form>\n""" % \
                    (feed["feed_link"],)

        dic = {}
        top_words = utils.top_words(articles = self.mongo.get_articles_from_collection(feed_id), n=50, size=int(word_size))
        html += "</br /><h1>Tag cloud</h1>\n<br />\n"
        # Tags cloud
        html += 'Minimum size of a word:'
        html += """<form method=get action="/feed/%s">""" % (feed["feed_id"],)
        html += """<input type="number" name="word_size" value="%s" min="2" max="15" step="1" size="2">""" % (word_size,)
        html += '<input type="submit" value="OK"></form>\n'
        html += '<div style="width: 35%; overflow:hidden; text-align: justify">' + \
                    utils.tag_cloud(top_words) + '</div>'

        html += "<br />"
        html += "<hr />"
        html += htmlfooter
        return html

    feed.exposed = True


    def articles(self, feed_id):
        """
        This page displays all articles of a feed.
        """
        try:
            feed = self.mongo.get_collection(feed_id)
            articles = self.mongo.get_articles_from_collection(feed_id)
        except KeyError:
            return self.error_page("This feed do not exists.")
        html = htmlheader()
        html += htmlnav
        html += """<div class="right inner">\n"""
        html += """<a href="/mark_as_read/Feed:%s">Mark all articles from this feed as read</a>""" % (feed_id,)
        html += """<br />\n<form method=get action="/q/%s"><input type="search" name="querystring" value="" placeholder="Search this feed" maxlength=2048 autocomplete="on"></form>\n""" % ("Feed:"+feed_id,)
        html += "<hr />\n"
        html += self.create_list_of_feeds()
        html += """</div> <div class="left inner">"""
        html += """<h1>Articles of the feed <i>%s</i></h1><br />""" % (feed["feed_title"],)

        for article in articles:

            if article["article_readed"] == False:
                # not readed articles are in bold
                not_read_begin, not_read_end = "<b>", "</b>"
            else:
                not_read_begin, not_read_end = "", ""

            if article["article_like"] == True:
                like = """ <img src="/img/heart.png" title="I like this article!" />"""
            else:
                like = ""

            # descrition for the CSS ToolTips
            article_content = utils.clear_string(article["article_content"])
            if article_content:
                description = " ".join(article_content[:500].split(' ')[:-1])
            else:
                description = "No description."

            # a description line per article (date, title of the article and
            # CSS description tooltips on mouse over)
            html += str(article["article_date"]) + " - " + \
                    """<a class="tooltip" href="/article/%s:%s" rel="noreferrer" target="_blank">%s%s%s<span class="classic">%s</span></a>""" % \
                            (feed_id, article["article_id"], not_read_begin, \
                            article["article_title"][:150], not_read_end, description) + like + "<br />\n"

        html += """\n<h4><a href="/">All feeds</a></h4>"""
        html += "<hr />\n"
        html += htmlfooter
        return html

    articles.exposed = True


    def unread(self, feed_id=""):
        """
        This page displays all unread articles of a feed.
        """
        feeds = self.mongo.get_all_collections()
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        if self.mongo.nb_unread_articles() != 0:

            # List unread articles of all the database
            if feed_id == "":
                html += "<h1>Unread article(s)</h1>"
                html += """\n<br />\n<a href="/mark_as_read/">Mark articles as read</a>\n<hr />\n"""
                for feed in feeds:
                    new_feed_section = True
                    nb_unread = 0

                    # For all unread article of the current feed.
                    for article in self.mongo.get_articles_from_collection(feed["feed_id"], condition=("article_readed", False)):
                        nb_unread += 1
                        if new_feed_section is True:
                            new_feed_section = False
                            html += """<h2><a name="%s"><a href="%s" rel="noreferrer" target="_blank">%s</a></a><a href="%s" rel="noreferrer" target="_blank"><img src="%s" width="28" height="28" /></a></h2>\n""" % \
                                (feed["feed_id"], feed["site_link"], feed["feed_title"], feed["feed_link"], feed["feed_image"])

                        # descrition for the CSS ToolTips
                        article_content = utils.clear_string(article["article_content"])
                        if article_content:
                            description = " ".join(article_content[:500].split(' ')[:-1])
                        else:
                            description = "No description."

                        # a description line per article (date, title of the article and
                        # CSS description tooltips on mouse over)
                        html += str(article["article_date"]) + " - " + \
                                """<a class="tooltip" href="/article/%s:%s" rel="noreferrer" target="_blank">%s<span class="classic">%s</span></a><br />\n""" % \
                                        (feed["feed_id"], article["article_id"], article["article_title"][:150], description)

                        if nb_unread == self.mongo.nb_unread_articles(feed["feed_id"]):
                            html += """<br />\n<a href="/mark_as_read/Feed:%s">Mark all articles from this feed as read</a>\n""" % \
                                        (feed["feed_id"],)
                html += """<hr />\n<a href="/mark_as_read/">Mark articles as read</a>\n"""

            # List unread articles of a feed
            else:
                try:
                    feed = self.mongo.get_collection(feed_id)
                except:
                    self.error_page("This feed do not exists.")
                html += """<h1>Unread article(s) of the feed <a href="/articles/%s">%s</a></h1>
                    <br />""" % (feed_id, feed["feed_title"])

                # For all unread article of the feed.
                for article in self.mongo.get_articles_from_collection(feed_id, condition=("article_readed", False)):
                    # descrition for the CSS ToolTips
                    article_content = utils.clear_string(article["article_content"])
                    if article_content:
                        description = " ".join(article_content[:500].split(' ')[:-1])
                    else:
                        description = "No description."

                    # a description line per article (date, title of the article and
                    # CSS description tooltips on mouse over)
                    html += str(article["article_date"]) + " - " + \
                            """<a class="tooltip" href="/article/%s:%s" rel="noreferrer" target="_blank">%s<span class="classic">%s</span></a><br />\n""" % \
                                    (feed_id, article["article_id"], article["article_title"][:150], description)

                html += """<hr />\n<a href="/mark_as_read/Feed:%s">Mark all as read</a>""" % (feed_id,)
        # No unread article
        else:
            html += '<h1>No unread article(s)</h1>\n<br />\n<a href="/fetch/">Why not check for news?</a>'
        html += """\n<h4><a href="/">All feeds</a></h4>"""
        html += "<hr />\n"
        html += htmlfooter
        return html

    unread.exposed = True


    def history(self, querystring="all", m=""):
        """
        This page enables to browse articles chronologically.
        """
        feeds = self.mongo.get_all_collections()
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">\n"""

        # Get the date from the tag cloud
        # Format: /history/?querystring=year:2011-month:06 to get the
        # list of articles of June, 2011.
        if m != "":
            querystring = """year:%s-month:%s""" % tuple(m.split('-'))

        if querystring == "all":
            html += "<h1>Search with tags cloud</h1>\n"
            html += "<h4>Choose a year</h4></br >\n"
        if "year" in querystring:
            the_year = querystring.split('-')[0].split(':')[1]
            if "month" not in querystring:
                html += "<h1>Choose a month for " + the_year + "</h1></br >\n"
        if "month" in querystring:
            the_month = querystring.split('-')[1].split(':')[1]
            html += "<h1>Articles of "+ calendar.month_name[int(the_month)] + \
                    ", "+ the_year +".</h1><br />\n"

        timeline = Counter()
        for feed in feeds:
            new_feed_section = True
            for article in self.mongo.get_articles_from_collection(feed["feed_id"]):

                if querystring == "all":
                    timeline[str(article["article_date"]).split(' ')[0].split('-')[0]] += 1

                elif querystring[:4] == "year":

                    if str(article["article_date"]).split(' ')[0].split('-')[0] == the_year:
                        timeline[str(article["article_date"]).split(' ')[0].split('-')[1]] += 1

                        if "month" in querystring:
                            if str(article["article_date"]).split(' ')[0].split('-')[1] == the_month:
                                if article["article_readed"] == False:
                                    # not readed articles are in bold
                                    not_read_begin, not_read_end = "<b>", "</b>"
                                else:
                                    not_read_begin, not_read_end = "", ""

                                if article["article_like"] == True:
                                    like = """ <img src="/img/heart.png" title="I like this article!" />"""
                                else:
                                    like = ""
                                # Descrition for the CSS ToolTips
                                article_content = utils.clear_string(article["article_content"])
                                if article_content:
                                    description = " ".join(article_content[:500].split(' ')[:-1])
                                else:
                                    description = "No description."
                                # Title of the article
                                article_title = article["article_title"]
                                if len(article_title) >= 110:
                                    article_title = article_title[:110] + " ..."

                                if new_feed_section is True:
                                    new_feed_section = False
                                    html += """<h2><a name="%s"><a href="%s" rel="noreferrer"
                                    target="_blank">%s</a></a><a href="%s" rel="noreferrer"
                                    target="_blank"><img src="%s" width="28" height="28" /></a></h2>\n""" % \
                                        (feed["feed_id"], feed["feed_link"], feed["feed_title"], feed["feed_link"], feed["feed_image"])

                                html += str(article["article_date"]).split(' ')[0][-2:] + " (" + \
                                        str(article["article_date"]).split(' ')[1]  + ") - " + \
                                        """<a class="tooltip" href="/article/%s:%s" rel="noreferrer" target="_blank">%s%s%s<span class="classic">%s</span></a>""" % \
                                                (feed["feed_id"], article["article_id"], not_read_begin, \
                                                article_title, not_read_end, description) + like + "<br />\n"
        if querystring == "all":
            query = "year"
        elif "year" in querystring:
            query = "year:" + the_year + "-month"
        if "month" not in querystring:
            html += '<div style="width: 35%; overflow:hidden; text-align: justify">' + \
                        utils.tag_cloud([(elem, timeline[elem]) for elem in timeline.keys()], query) + '</div>'
        html += '<br /><br /><h1>Search with a month+year picker</h1>\n'
        html += '<form>\n\t<input name="m" type="month">\n\t<input type="submit" value="Go">\n</form>'
        html += '<hr />'
        html += htmlfooter
        return html

    history.exposed = True


    def plain_text(self, target):
        """
        Display an article in plain text (without HTML tags).
        """
        try:
            feed_id, article_id = target.split(':')
            feed, article = self.feeds[feed_id], self.feeds[feed_id].articles[article_id]
        except:
            return self.error_page("Bad URL. This article do not exists.")
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        html += """<h1><i>%s</i> from <a href="/articles/%s">%s</a></h1>\n<br />\n"""% \
                            (article.article_title, feed_id, feed.feed_title)
        description = utils.clear_string(article.article_description)
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


    def mark_as_read(self, target=""):
        """
        Mark one (or more) article(s) as read by setting the value of the field
        'article_readed' of the MongoDB database to 'True'.
        """
        param, _, identifiant = target.partition(':')

        # Mark all articles as read.
        if param == "":
            self.mongo.mark_as_read(True, None, None)
        # Mark all articles from a feed as read.
        elif param == "Feed" or param == "Feed_FromMainPage":
            self.mongo.mark_as_read(True, identifiant, None)
        # Mark an article as read.
        elif param == "Article":
            self.mongo.mark_as_read(True, identifiant.split(':')[1], identifiant.split(':')[0])
        if param == "" or param == "Feed_FromMainPage":
            return self.index()
        elif param == "Feed":
            return self.articles(identifiant)

    mark_as_read.exposed = True


    def notifications(self):
        """
        List all active e-mail notifications.
        """
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        feeds = self.mongo.get_all_collections(condition=("mail",True))
        if feeds != []:
            html += "<h1>You are receiving e-mails for the following feeds:</h1>\n"
            for feed in feeds:
                html += """\t<a href="/articles/%s">%s</a> - <a href="/mail_notification/0:%s">Stop</a><br />\n""" % \
                        (feed["feed_id"], feed.feed_title, feed.feed_id)
        else:
            html += "<p>No active notifications.<p>\n"
        html += """<p>Notifications are sent to: <a href="mail:%s">%s</a></p>""" % \
                        (utils.mail_to, utils.mail_to)
        html += "\n<hr />\n" + htmlfooter
        return html

    notifications.exposed = True


    def mail_notification(self, param):
        """
        Enable or disable to notifications of news for a feed.
        """
        try:
            action, feed_id = param.split(':')
            feed = self.feeds[feed_id]
        except:
            return self.error_page("Bad URL. This feed do not exists.")

        return self.index()

    mail_notification.exposed = True


    def like(self, param):
        """
        Mark or unmark an article as favorites.
        """
        try:
            like, feed_id, article_id = param.split(':')
            articles = self.mongo.get_article(feed_id, article_id)
        except:
            return self.error_page("Bad URL. This article do not exists.")
        self.mongo.like_article("1"==like, feed_id, article_id)
        return self.article(feed_id+":"+article_id)

    like.exposed = True


    def favorites(self):
        """
        List of favorites articles
        """
        feeds = self.mongo.get_all_collections()
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        html += "<h1>Your favorites articles</h1>"
        for feed in feeds:
            new_feed_section = True
            for article in self.mongo.get_articles_from_collection(feed["feed_id"]):
                if article["article_like"] == True:
                    if new_feed_section is True:
                        new_feed_section = False
                        html += """<h2><a name="%s"><a href="%s" rel="noreferrer"target="_blank">%s</a></a><a href="%s" rel="noreferrer" target="_blank"><img src="%s" width="28" height="28" /></a></h2>\n""" % \
                            (feed["feed_id"], feed["feed_link"], feed["feed_title"], feed["feed_link"], feed["feed_image"])

                    # descrition for the CSS ToolTips
                    article_content = utils.clear_string(article["article_content"])
                    if article_content:
                        description = " ".join(article_content[:500].split(' ')[:-1])
                    else:
                        description = "No description."

                    # a description line per article (date, title of the article and
                    # CSS description tooltips on mouse over)
                    html += str(article["article_date"]) + " - " + \
                            """<a class="tooltip" href="/article/%s:%s" rel="noreferrer" target="_blank">%s<span class="classic">%s</span></a><br />\n""" % \
                                    (feed["feed_id"], article["article_id"], article["article_title"][:150], description)
        html += "<hr />\n"
        html += htmlfooter
        return html

    favorites.exposed = True


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
        # if the feed is not in the file feed.lst
        if result is False:
            html +=  "<p>You are already following this feed!</p>"
        else:
            html += """<p>Feed added. You can now <a href="/fetch/">fetch your feeds</a>.</p>"""
        html += """\n<br />\n<a href="/management/">Back to the management page.</a><br />\n"""
        html += "<hr />\n"
        html += htmlfooter
        return html

    add_feed.exposed = True


    def remove_feed(self, feed_id):
        """
        Remove a feed from the file feed.lst and from the MongoDB database.
        """
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""

        feed = self.mongo.get_collection(feed_id)
        self.mongo.delete_feed(feed_id)
        utils.remove_feed(feed["feed_link"])

        html += """<p>All articles from the feed <i>%s</i> are now removed from the base.</p><br />""" % \
                (feed["feed_title"],)
        html += """<a href="/management/">Back to the management page.</a><br />\n"""
        html += "<hr />\n"
        html += htmlfooter
        return html

    remove_feed.exposed = True


    def change_feed_url(self, new_feed_url, old_feed_url):
        """
        Enables to change the URL of a feed already present in the database.
        """
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        utils.change_feed_url(old_feed_url, new_feed_url)
        html += "<p>The URL of the feed has been changed.</p>"
        html += "<hr />\n"
        html += htmlfooter
        return html

    change_feed_url.exposed = True

    def change_feed_name(self, feed_url, new_feed_name):
        """
        Enables to change the name of a feed.
        """
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        utils.change_feed_name(feed_url, new_feed_name)
        html += "<p>The name of the feed has been changed.</p>"
        html += "<hr />\n"
        html += htmlfooter
        return html

    change_feed_name.exposed = True

    def change_feed_logo(self, feed_url, new_feed_logo):
        """
        Enables to change the name of a feed.
        """
        html = htmlheader()
        html += htmlnav
        html += """<div class="left inner">"""
        utils.change_feed_logo(feed_url, new_feed_logo)
        html += "<p>The logo of the feed has been changed.</p>"
        html += "<hr />\n"
        html += htmlfooter
        return html

    change_feed_logo.exposed = True


    def set_max_articles(self, max_nb_articles=1):
        """
        Enables to set the maximum of articles to be loaded per feed from
        the data base.
        """
        if max_nb_articles < -1 or max_nb_articles == 0:
            max_nb_articles = 1
        utils.MAX_NB_ARTICLES = int(max_nb_articles)
        return self.management()

    set_max_articles.exposed = True


    def delete_article(self, param):
        """
        Delete an article.
        """
        try:
            feed_id, article_id = param.split(':')
            self.mongo.delete_article(feed_id, article_id)
        except:
            return self.error_page("Bad URL. This article do not exists.")

        return self.index()

    delete_article.exposed = True


    def drop_base(self):
        """
        Delete all articles.
        """
        utils.drop_base()
        return self.management()

    drop_base.exposed = True


    def export(self, export_method):
        """
        Export articles currently loaded from the MongoDB database with
        the appropriate function of the 'export' module.
        """
        try:
            getattr(export, export_method)(self.feeds)
        except Exception, e:
            return self.error_page(e)
        return self.management()

    export.exposed = True


    def epub(self, param):
        """
        Export an article to EPUB.
        """
        try:
            from epub import ez_epub
        except Exception, e:
            return self.error_page(e)
        try:
            feed_id, article_id = param.split(':')
        except:
            return self.error_page("Bad URL.")
        try:
            feed = self.feeds[feed_id]
            article = feed.articles[article_id]
        except:
            self.error_page("This article do not exists.")
        try:
            folder = utils.path + "/var/export/epub/"
            os.makedirs(folder)
        except OSError:
            # directories already exists (not a problem)
            pass
        section = ez_epub.Section()
        section.title = article.article_title.decode('utf-8')
        section.paragraphs = [utils.clear_string(article.article_description).decode('utf-8')]
        ez_epub.makeBook(article.article_title.decode('utf-8'), [feed.feed_title.decode('utf-8')], [section], \
                os.path.normpath(folder) + "article.epub", lang='en-US', cover=None)
        return self.article(param)

    epub.exposed = True


if __name__ == '__main__':
    # Point of entry in execution mode
    print "Launching pyAggr3g470r..."

    root = Root()
    root.favicon_ico = cherrypy.tools.staticfile.handler(filename=os.path.join(utils.path + "/img/favicon.png"))
    cherrypy.config.update({ 'server.socket_port': 12556, 'server.socket_host': "0.0.0.0"})
    cherrypy.config.update({'error_page.404': error_page_404})
    _cp_config = {'request.error_response': handle_error}

    cherrypy.quickstart(root, "/" ,config=utils.path + "/cfg/cherrypy.cfg")
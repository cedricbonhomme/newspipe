#! /usr/local/bin/python
#-*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2010/03/01 $"
__copyright__ = "Copyright (c) 2010 Cedric Bonhomme"
__license__ = "GPLv3"

import os
import time
import sqlite3
import cherrypy
import threading

from cherrypy.lib.static import serve_file

import utils
import feedgetter

bindhost = "0.0.0.0"

cherrypy.config.update({ 'server.socket_port': 12556, 'server.socket_host': bindhost})

path = {'/css/style.css': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'css/style.css'}, \
        '/css/img/feed-icon-28x28.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'css/img/feed-icon-28x28.png'}, \
        '/css/img/delicious.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'css/img/delicious.png'}, \
        '/css/img/digg.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'css/img/digg.png'}, \
        '/css/img/reddit.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'css/img/reddit.png'}, \
        '/css/img/scoopeo.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'css/img/scoopeo.png'}, \
        '/css/img/blogmarks.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'css/img/blogmarks.png'}, \
        '/var/histogram.png':{'tools.staticfile.on': True, \
                'tools.staticfile.filename':utils.path+'var/histogram.png'}}

htmlheader = '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n' + \
            '<head>' + \
            '\n\t<title>pyAggr3g470r - RSS Feed Reader</title>\n' + \
            '\t<link rel="stylesheet" type="text/css" href="/css/style.css" />' + \
            '\n\t<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n' + \
            '</head>\n'

htmlfooter = '<p>This software is under GPLv3 license. You are welcome to copy, modify or' + \
            ' redistribute the source code according to the' + \
            ' <a href="http://www.gnu.org/licenses/gpl-3.0.txt">GPLv3</a> license.</p></div>\n' + \
            '</body>\n</html>'

htmlnav = '<body>\n<h1><a name="top"><a href="/">pyAggr3g470r - RSS Feed Reader</a></a></h1>\n<a' + \
        ' href="http://bitbucket.org/cedricbonhomme/pyaggr3g470r/" rel="noreferrer" target="_blank">' + \
        'pyAggr3g470r (source code)</a>'


class Root:
    def index(self):
        """
        Main page containing the list of feeds and articles.
        """
        html = htmlheader
        html += htmlnav
        html += """<div class="right inner">\n"""
        html += """<a href="/management/">Management</a><br />\n"""
        html += """<a href="/fetch/">Fetch all feeds</a><br />\n"""
        html += """<a href="/mark_as_read/All:">Mark articles as read</a>\n"""
        html += """<form method=get action="/q/"><input type="text" name="querystring" value=""><input
        type="submit" value="Search"></form>\n"""
        html += "<hr />\n"
        html += """Your feeds (%s):<br />\n""" % len(self.articles.keys())
        for rss_feed_id in self.articles.keys():

            if self.feeds[rss_feed_id][1] != 0:
                # not readed articles are in bold
                not_read_begin = "<b>"
                not_read_end = "</b>"
            else:
                not_read_begin = ""
                not_read_end = ""

            html += """<a href="/#%s">%s</a> (<a href="/unread/%s"
                    title="Unread article(s)">%s%s%s</a> / %s)<br />\n""" % \
                            (rss_feed_id.encode('utf-8'), \
                            self.feeds[rss_feed_id][3].encode('utf-8'), \
                            rss_feed_id, not_read_begin, \
                            self.feeds[rss_feed_id][1], not_read_end, \
                            self.feeds[rss_feed_id][0])

        html += """</div>\n<div class="left inner">\n"""

        for rss_feed_id in self.articles.keys():
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

                html += article[1].encode('utf-8') + \
                        " - " + not_read_begin + \
                        """<a href="/description/%s:%s" rel="noreferrer" target="_blank">%s</a>""" % \
                                (rss_feed_id, article[0].encode('utf-8'), article[2].encode('utf-8')) + \
                        not_read_end + \
                        "<br />\n"
            html += "<br />\n"

            html += """<a href="/all_articles/%s">All articles</a>""" % (rss_feed_id,)
            html += """ <a href="/mark_as_read/Feed_FromMainPage:%s">Mark all as read</a>""" % (rss_feed_id,)
            if self.feeds[rss_feed_id][1] != 0:
                html += """ <a href="/unread/%s" title="Unread article(s)"
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


    def management(self):
        """
        Management of articles.
        """
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">\n"""
        html += "<h1>Add Feeds</h1>\n"
        html += """<form method=get action="add_feed/"><input type="text" name="v" value="">\n<input
        type="submit" value="OK"></form>\n"""

        if self.articles:
            html += "<h1>Delete Feeds</h1>\n"
            html += """<form method=get action="del_feed/"><select name="feed_list">\n"""
            for feed_id in self.articles.keys():
                html += """\t<option value="%s">%s</option>\n""" % \
                        (feed_id, self.feeds[feed_id][3].encode('utf-8'))
            html += """</select></form>\n"""

        html += "<hr />\n"
        html += """<p>The database contains a total of %s article(s) with
                <a href="/unread/All">%s unread article(s)</a>.<br />""" % \
                    (self.nb_articles, sum([feed[1] for feed in self.feeds.values()]))
        html += """Database: %s.\n<br />Size: %s bytes.</p>\n""" % \
                    (os.path.abspath(utils.sqlite_base), os.path.getsize(utils.sqlite_base))

        html += """<form method=get action="/fetch/">\n<input
        type="submit" value="Fetch all feeds"></form>\n"""
        html += """<form method=get action="add_feed/">\n<input
        type="submit" value="Delete all articles"></form>\n"""

        html += "<hr />\n"
        if self.articles:
            html += "<h1>Statistics</h1>\n"
            if "oice" not in utils.IMPORT_ERROR:
                nb_french = 0
                nb_english = 0
                for rss_feed_id in self.articles.keys():
                    for article in self.articles[rss_feed_id]:
                        if article[6] == 'french':
                            nb_french += 1
                        elif article[6] == 'english':
                            nb_english += 1
                nb_other = self.nb_articles - nb_french - nb_english

            html += "<table border=0>\n<tr><td>"
            html += "<h3>Words count</h3>\n"
            html += "<ol>\n"
            for word, frequency in self.top_words:
                html += """\t<li><a href="/q/?querystring=%s">%s</a>: %s</li>\n""" % \
                                (word, word, frequency)
            html += "</ol>\n"
            html += "<h3>Languages</h3>\n"
            if "oice" in utils.IMPORT_ERROR:
                html += "Install the module "
                html += """<a href="http://pypi.python.org/pypi/oice.langdet/">oice.langdet</a>"""
                html += "</td>\n<td>"
            else:
                html += "<ul>\n"
                for language in ['english', 'french', 'other']:
                    html += """\t<li>%s articles in <a href="/language/%s">%s</a></li>\n""" % \
                                    (locals()["nb_"+language], language, language)
                html += "</ul>\n</td>\n<td>"
            html += """<img src="/var/histogram.png" /></td></tr></table>"""

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
        feed_id = None
        if param == "Feed":
            feed_id, _, querystring = value.partition(':')
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">"""

        html += """<h1>Articles containing the string <i>%s</i></h1><br />""" % (querystring,)

        if feed_id is not None:
            for article in self.articles[rss_feed_id]:
                article_content = utils.remove_html_tags(article[4].encode('utf-8'))
                if not article_content:
                    utils.remove_html_tags(article[2].encode('utf-8'))
                if querystring.lower() in article_content.lower():
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
                            not_read_end
        else:
            for rss_feed_id in self.articles.keys():
                for article in self.articles[rss_feed_id]:
                    article_content = utils.remove_html_tags(article[4].encode('utf-8'))
                    if not article_content:
                        utils.remove_html_tags(article[2].encode('utf-8'))
                    if querystring.lower() in article_content.lower():
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
                                not_read_end + """ from <i><a href="%s">%s</a></i><br />\n""" % \
                                        (self.feeds[rss_feed_id][5].encode('utf-8'), \
                                        self.feeds[rss_feed_id][3].encode('utf-8'))
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
        #self.update()
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
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">"""
        for article in articles_list:
            if article_id == article[0]:

                if article[5] == "0":
                    self.mark_as_read("Article:"+article[3]) # update the database

                html += """<h1><i>%s</i> from <a href="/all_articles/%s">%s</a></h1>\n<br />\n""" % \
                                (article[2].encode('utf-8'), feed_id, \
                                self.feeds[feed_id][3].encode('utf-8'))
                description = article[4].encode('utf-8')
                if description:
                    html += description
                else:
                    html += "No description available."
                html += "\n<hr />\n"
                html += """This article seems to be written in <a href="/language/%s">%s</a>.\n""" % \
                                (article[6], article[6])
                html += """<br />\n<a href="/plain_text/%s:%s">Plain text</a>\n""" % \
                                (feed_id, article_id)
                html += """<br />\n<a href="%s">Complete story</a>\n<br />\n""" % \
                                (article[3].encode('utf-8'),)
                # Share this article:
                # on delicious
                html += """<a href="http://delicious.com/post?url=%s&title=%s"
                        rel="noreferrer" target="_blank">\n
                        <img src="/css/img/delicious.png" title="Share on del.iciou.us" /></a> &nbsp;&nbsp; """ % \
                                (article[3].encode('utf-8'), article[2].encode('utf-8'))
                # on Digg
                html += """<a href="http://digg.com/submit?url=%s&title=%s"
                        rel="noreferrer" target="_blank">\n
                        <img src="/css/img/digg.png" title="Share on Digg" /></a> &nbsp;&nbsp; """ % \
                                (article[3].encode('utf-8'), article[2].encode('utf-8'))
                # on reddit
                html += """<a href="http://reddit.com/submit?url=%s&title=%s"
                        rel="noreferrer" target="_blank">\n
                        <img src="/css/img/reddit.png" title="Share on reddit" /></a> &nbsp;&nbsp; """ % \
                                (article[3].encode('utf-8'), article[2].encode('utf-8'))
                # on Scoopeo
                html += """<a href="http://scoopeo.com/scoop/new?newurl=%s&title=%s"
                        rel="noreferrer" target="_blank">\n
                        <img src="/css/img/scoopeo.png" title="Share on Scoopeo" /></a> &nbsp;&nbsp; """ % \
                                (article[3].encode('utf-8'), article[2].encode('utf-8'))
                # on Blogmarks
                html += """<a href="http://blogmarks.net/my/new.php?url=%s&title=%s"
                        rel="noreferrer" target="_blank">\n
                        <img src="/css/img/blogmarks.png" title="Share on Blogmarks" /></a>""" % \
                                (article[3].encode('utf-8'), article[2].encode('utf-8'))
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
        html = htmlheader
        html += htmlnav
        html += """<div class="right inner">\n"""
        html += """<a href="/mark_as_read/Feed:%s">Mark all articles from this feed as read</a>""" % (feed_id,)
        html += """<br />\n<form method=get action="/q/Feed"><input type="text" name="Feed:%s:querystring" value=""><input
        type="submit" value="Search this feed"></form>\n""" % (feed_id,)
        html += "<hr />\n"
        html += """Your feeds (%s):<br />\n""" % len(self.articles.keys())
        for rss_feed_id in self.articles.keys():

            html += """<a href="/#%s">%s</a> (<a href="/unread/%s" title="Unread article(s)">%s</a> / %s)<br />\n""" % \
                                (rss_feed_id.encode('utf-8'), \
                                self.feeds[rss_feed_id][3].encode('utf-8'), \
                                rss_feed_id, self.feeds[rss_feed_id][1], \
                                self.feeds[rss_feed_id][0])
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

            html += article[1].encode('utf-8') + \
                    " - " + not_read_begin + \
                    """<a href="/description/%s:%s" rel="noreferrer" target="_blank">%s</a>""" % \
                            (feed_id, article[0].encode('utf-8'), \
                            utils.remove_html_tags(article[2].encode('utf-8'))) + \
                    not_read_end + \
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
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">"""

        if feed_id == "All":
            html += "<h1>Unread article(s)</h1>"
            for rss_feed_id in self.feeds.keys():
                for article in self.articles[rss_feed_id]:
                    if article[5] == "0":
                        html += article[1].encode('utf-8') + \
                                """ - <a href="/description/%s:%s" rel="noreferrer" target="_blank">%s</a>
                                from <i><a href="%s">%s</a></i><br />\n""" % \
                                        (rss_feed_id, article[0].encode('utf-8'), article[2].encode('utf-8'), \
                                        self.feeds[rss_feed_id][5].encode('utf-8'), \
                                        self.feeds[rss_feed_id][3].encode('utf-8'))
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
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">"""
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
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">"""
        feed_id, article_id = target.split(':')
        for article in articles_list:
            if article_id == article[0]:
                html += """<h1><i>%s</i> from <a href="/all_articles/%s">%s</a></h1>\n<br />\n"""% \
                                    (article[2].encode('utf-8'), feed_id, \
                                    self.feeds[feed_id][3].encode('utf-8'))
                description = utils.remove_html_tags(article[4].encode('utf-8'))
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
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">"""
        html += """%s""" % message
        html += "\n<hr />\n" + htmlfooter
        return html

    error_page.exposed = True


    def mark_as_read(self, target):
        """
        Mark one (or more) article(s) as read by setting the value of the field
        'article_readed' of the SQLite database to 1.
        """
        LOCKER.acquire()
        param, _, identifiant = target.partition(':')
        try:
            conn = sqlite3.connect(utils.sqlite_base, isolation_level = None)
            c = conn.cursor()
            # Mark all articles as read.
            if param == "All":
                c.execute("UPDATE articles SET article_readed=1")
            # Mark all articles from a feed as read.
            elif param == "Feed" or param == "Feed_FromMainPage":
                c.execute("UPDATE articles SET article_readed=1 WHERE feed_link='" + \
                            self.feeds[identifiant][4].encode('utf-8') + "'")
            # Mark an article as read.
            elif param == "Article":
                c.execute("UPDATE articles SET article_readed=1 WHERE article_link='" + \
                            identifiant + "'")
            conn.commit()
            c.close()
        except Exception:
            self.error_page("Impossible to mark this article as read (database error).")

        #threading.Thread(None, self.update, None, ()).start()

        if param == "All" or param == "Feed_FromMainPage":
            return self.index()
        elif param == "Feed":
            return self.all_articles(identifiant)
        LOCKER.release()

    mark_as_read.exposed = True


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


    def update(self, path=None, event = None):
        """
        Synchronizes transient objects with the database,
        computes the list of most frequent words and generates the histogram.
        Called when an article is marked as read or when new articles are fetched.
        """
        self.articles, self.feeds = utils.load_feed()
        self.nb_articles = sum([feed[0] for feed in self.feeds.values()])
        if self.articles != {}:
            self.top_words = utils.top_words(self.articles, 10)
            if "pylab" not in utils.IMPORT_ERROR:
                utils.create_histogram(self.top_words)
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
            old_size = 0
            try:
                print "Watching %s" % utils.sqlite_base
                while True:
                    time.sleep(2)
                    # very simple test
                    if os.path.getsize(utils.sqlite_base) != old_size:
                        print "The base of feeds (%s) has changed.\nReloading..." % utils.sqlite_base
                        self.update()
                        old_size = os.path.getsize(utils.sqlite_base)
            except KeyboardInterrupt:
                pass
            print "Stop watching", utils.sqlite_base


if __name__ == '__main__':
    # Point of entry in execution mode
    LOCKER = threading.Lock()
    root = Root()
    if not os.path.isfile(utils.sqlite_base):
        # create the SQLite base if not exists
        utils.create_base()
    # load the informations from base in memory
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
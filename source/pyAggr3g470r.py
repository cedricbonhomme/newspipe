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
__version__ = "$Revision: 3.6 $"
__date__ = "$Date: 2010/01/29 $"
__revision__ = "$Date: 2012/12/04 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

#
# This file contains the "Root" class which describes
# all pages (views) of pyAggr3g470r. These pages are:
# - main page;
# - management;
# - history;
# - favorites;
# - notifications;
# - unread;
# - feed summary.
# Templates are described in ./templates with the Mako
# template library.
#

import os
import re
import datetime
import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['templates'])

import conf
import utils
import export
import mongodb
import feedgetter
from auth import AuthController, require, member_of, name_is
#from qrcode.pyqrnative.PyQRNative import QRCode, QRErrorCorrectLevel, CodeOverflowException
#from qrcode import qr


def error_404(status, message, traceback, version):
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

def htmlheader(text=""):
    """
    Return the header of the HTML page with the number of unread articles
    in the 'title' HTML tag..
    """
    return '<!DOCTYPE html>\n' + \
        '<head>' + \
        '\n\t<title>'+ text +' - pyAggr3g470r - News aggregator</title>\n' + \
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
        '</div><a name="top"><a href="/">pyAggr3g470r - News aggregator</a></a></h1>\n'

class RestrictedArea(object):
    """
    All methods in this controller (and subcontrollers) is
    open only to members of the admin group
    """
    _cp_config = {
        'auth.require': [member_of('admin')]
    }

    @cherrypy.expose
    def index(self):
        return """This is the admin only area."""

class pyAggr3g470r(object):
    """
    Main class.
    All pages of pyAggr3g470r are described in this class.
    """
    _cp_config = {'request.error_response': handle_error, \
                    'tools.sessions.on': True, \
                    'tools.auth.on': True}

    def __init__(self):
        """
        """
        self.auth = AuthController()
        restricted = RestrictedArea()

        self.mongo = mongodb.Articles(conf.MONGODB_ADDRESS, conf.MONGODB_PORT, \
                        conf.MONGODB_DBNAME, conf.MONGODB_USER, conf.MONGODB_PASSWORD)
    @require()
    def index(self):
        """
        Main page containing the list of feeds and articles.
        """
        feeds = self.mongo.get_all_feeds()
        nb_unread_articles = self.mongo.nb_unread_articles()
        nb_favorites = self.mongo.nb_favorites()
        nb_mail_notifications = self.mongo.nb_mail_notifications()
        tmpl = lookup.get_template("index.html")
        return tmpl.render(feeds=feeds, nb_feeds=len(feeds), mongo=self.mongo, \
                            nb_favorites=nb_favorites, nb_unread_articles=nb_unread_articles, \
                            nb_mail_notifications=nb_mail_notifications, header_text=nb_unread_articles)

    index.exposed = True

    @require()
    def management(self):
        """
        Management page.
        Allows adding and deleting feeds. Export functions of the MongoDB data base
        and display some statistics.
        """
        feeds = self.mongo.get_all_feeds()
        nb_mail_notifications = self.mongo.nb_mail_notifications()
        nb_favorites = self.mongo.nb_favorites()
        nb_articles = self.mongo.nb_articles()
        nb_unread_articles = self.mongo.nb_unread_articles()
        tmpl = lookup.get_template("management.html")
        return tmpl.render(feeds=feeds, nb_mail_notifications=nb_mail_notifications, \
                            nb_favorites=nb_favorites, nb_articles=nb_articles, \
                            nb_unread_articles=nb_unread_articles)

    management.exposed = True

    @require()
    def statistics(self, word_size=6):
        """
        More advanced statistics.
        """
        articles = self.mongo.get_articles()
        top_words = utils.top_words(articles, n=50, size=int(word_size))
        tag_cloud = utils.tag_cloud(top_words)
        tmpl = lookup.get_template("statistics.html")
        return tmpl.render(articles=articles, word_size=word_size, tag_cloud=tag_cloud)

    statistics.exposed = True

    @require()
    def search(self, query=None):
        """
        Simply search for the string 'query'
        in the description of the article.
        """
        param, _, value = query.partition(':')
        wordre = re.compile(r'\b%s\b' % param, re.I)
        feed_id = None
        if param == "Feed":
            feed_id, _, query = value.partition(':')
        feeds = self.mongo.get_all_feeds()
        tmpl = lookup.get_template("search.html")
        return tmpl.render(feeds=feeds, feed_id=feed_id, query=query, \
                        wordre=wordre, mongo=self.mongo)

    search.exposed = True

    @require()
    def fetch(self):
        """
        Fetch all feeds.
        """
        feed_getter = feedgetter.FeedGetter()
        feed_getter.retrieve_feed()
        return self.index()

    fetch.exposed = True

    @require()
    def article(self, param):
        """
        Display the article in parameter in a new Web page.
        """
        try:
            feed_id, article_id = param.split(':')
            feed = self.mongo.get_feed(feed_id)
            articles = self.mongo.get_articles(feed_id)
            article = self.mongo.get_articles(feed_id, article_id)
        except:
            return self.error("Bad URL. This article do not exists.")

        if article["article_readed"] == False:
            # if the current article is not yet readed, update the database
            self.mark_as_read("Article:"+article["article_id"]+":"+feed["feed_id"])

        # Description (full content) of the article
        description = article["article_content"]
        if description:
            p = re.compile(r'<code><')
            q = re.compile(r'></code>')
            description = p.sub('<code>&lt;', description)
            description = q.sub('&gt;</code>', description)
            description = description + "\n<br /><br /><br />"
        else:
            description += "No description available.\n<br /><br /><br />"
        """
        # Generation of the QR Code for the current article
        try:
            os.makedirs("./var/qrcode/")
        except OSError:
            pass
        if not os.path.isfile("./var/qrcode/" + article_id + ".png"):
            # QR Code generation
            try:
                f = qr.QRUrl(url = article["article_link"])
                f.make()
            except:
                f = qr.QRUrl(url = "URL too long.")
                f.make()
            f.save("./var/qrcode/"+article_id+".png")
        """

        # Previous and following articles
        previous, following = None, None
        liste = self.mongo.get_articles(feed_id)
        for current_article in self.mongo.get_articles(feed_id):
            next(articles)
            if current_article["article_id"] == article_id:
                break
            following = current_article
        if following is None:
            following = liste[liste.count()-1]
        try:
            previous = next(articles)
        except StopIteration:
            previous = liste[0]

        tmpl = lookup.get_template("article.html")
        return tmpl.render(header_text=article["article_title"], article=article, previous=previous, following=following, \
                            diaspora=conf.DIASPORA_POD, feed=feed, description=description)

    article.exposed = True

    @require()
    def feed(self, feed_id, word_size=6):
        """
        This page gives summary informations about a feed (number of articles,
        unread articles, average activity, tag cloud, e-mail notification and
        favourite articles for the current feed.
        """
        try:
            feed = self.mongo.get_feed(feed_id)
            articles = self.mongo.get_articles(feed_id, limit=10)
            nb_articles_feed = self.mongo.nb_articles(feed_id)
            nb_articles_total = self.mongo.nb_articles()
            nb_unread_articles_feed = self.mongo.nb_unread_articles(feed_id)
        except KeyError:
            return self.error("This feed do not exists.")

        if articles != []:
            last_article = utils.string_to_datetime(str(articles[0]["article_date"]))
            first_article = utils.string_to_datetime(str(articles[self.mongo.nb_articles(feed_id)-2]["article_date"]))
            delta = last_article - first_article
            delta_today = datetime.datetime.fromordinal(datetime.date.today().toordinal()) - last_article
            average = round(float(nb_articles_feed) / abs(delta.days), 2)
            favorites = self.mongo.get_favorites(feed_id)
            top_words = utils.top_words(articles = self.mongo.get_articles(feed_id), n=50, size=int(word_size))
            tag_cloud = utils.tag_cloud(top_words)

        tmpl = lookup.get_template("feed.html")
        return tmpl.render(feed=feed, articles=articles, favorites=favorites, \
                            nb_articles_feed=nb_articles_feed, nb_articles_total=nb_articles_total, nb_unread_articles_feed=nb_unread_articles_feed, \
                            first_post_date=first_article, end_post_date=last_article, \
                            average=average, delta=delta, delta_today=delta_today, \
                            tag_cloud=tag_cloud, word_size=word_size, mail_to=conf.mail_to)

    feed.exposed = True

    @require()
    def articles(self, feed_id):
        """
        This page displays all articles of a feed.
        """
        try:
            feed = self.mongo.get_feed(feed_id)
            articles = self.mongo.get_articles(feed_id)
        except KeyError:
            return self.error("This feed do not exists.")
        tmpl = lookup.get_template("articles.html")
        return tmpl.render(articles=articles, feed=feed)

    articles.exposed = True

    @require()
    def unread(self, feed_id=""):
        """
        This page displays all unread articles of a feed.
        """
        feeds = self.mongo.get_all_feeds()
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
                    for article in self.mongo.get_articles(feed["feed_id"], condition=("article_readed", False)):
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
                        html += article["article_date"].strftime('%Y-%m-%d %H:%M') + " - " + \
                                """<a class="tooltip" href="/article/%s:%s" rel="noreferrer" target="_blank">%s<span class="classic">%s</span></a><br />\n""" % \
                                        (feed["feed_id"], article["article_id"], article["article_title"][:150], description)

                        if nb_unread == self.mongo.nb_unread_articles(feed["feed_id"]):
                            html += """<br />\n<a href="/mark_as_read/Feed:%s">Mark all articles from this feed as read</a>\n""" % \
                                        (feed["feed_id"],)
                html += """<hr />\n<a href="/mark_as_read/">Mark articles as read</a>\n"""

            # List unread articles of a feed
            else:
                try:
                    feed = self.mongo.get_feed(feed_id)
                except:
                    self.error("This feed do not exists.")
                html += """<h1>Unread article(s) of the feed <a href="/articles/%s">%s</a></h1>
                    <br />""" % (feed_id, feed["feed_title"])

                # For all unread article of the feed.
                for article in self.mongo.get_articles(feed_id, condition=("article_readed", False)):
                    # descrition for the CSS ToolTips
                    article_content = utils.clear_string(article["article_content"])
                    if article_content:
                        description = " ".join(article_content[:500].split(' ')[:-1])
                    else:
                        description = "No description."

                    # a description line per article (date, title of the article and
                    # CSS description tooltips on mouse over)
                    html += article["article_date"].strftime('%Y-%m-%d %H:%M') + " - " + \
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

    @require()
    def history(self, query="all", m=""):
        """
        This page enables to browse articles chronologically.
        """
        feeds = self.mongo.get_all_feeds()
        tmpl = lookup.get_template("history.html")
        return tmpl.render(feeds=feeds, mongo=self.mongo, query=query, m=m)

    history.exposed = True

    @require()
    def plain_text(self, target):
        """
        Display an article in plain text (without HTML tags).
        """
        try:
            feed_id, article_id = target.split(':')
            feed = self.mongo.get_feed(feed_id)
            article = self.mongo.get_articles(feed_id, article_id)
        except:
            return self.error("Bad URL. This article do not exists.")
        description = utils.clear_string(article["article_content"])
        if not description:
            description = "Unvailable"
        tmpl = lookup.get_template("plain_text.html")
        return tmpl.render(feed_title=feed["feed_title"], \
                           article_title=article["article_title"], \
                           description = description)

    plain_text.exposed = True

    @require()
    def error(self, message):
        """
        Display a message (bad feed id, bad article id, etc.)
        """
        tmpl = lookup.get_template("error.html")
        return tmpl.render(message=message)

    error.exposed = True

    @require()
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
        return self.index()

    mark_as_read.exposed = True

    @require()
    def notifications(self):
        """
        List all active e-mail notifications.
        """
        feeds = self.mongo.get_all_feeds(condition=("mail",True))
        tmpl = lookup.get_template("notifications.html")
        return tmpl.render(feeds=feeds, mail_to=conf.mail_to)

    notifications.exposed = True

    @require()
    def mail_notification(self, param):
        """
        Enable or disable to notifications of news for a feed.
        """
        try:
            action, feed_id = param.split(':')
        except:
            return self.error("Bad URL. This feed do not exists.")
        return self.index()

    mail_notification.exposed = True

    @require()
    def like(self, param):
        """
        Mark or unmark an article as favorites.
        """
        try:
            like, feed_id, article_id = param.split(':')
            articles = self.mongo.get_articles(feed_id, article_id)
        except:
            return self.error("Bad URL. This article do not exists.")
        self.mongo.like_article("1"==like, feed_id, article_id)
        return self.article(feed_id+":"+article_id)

    like.exposed = True

    @require()
    def favorites(self):
        """
        List of favorites articles
        """
        feeds = self.mongo.get_all_feeds()
        articles = {}
        for feed in feeds:
            articles[feed["feed_id"]] = self.mongo.get_favorites(feed["feed_id"])
        tmpl = lookup.get_template("favorites.html")
        return tmpl.render(feeds=feeds, \
                           articles=articles)

    favorites.exposed = True

    @require()
    def inactives(self, nb_days=365):
        """
        List of favorites articles
        """
        feeds = self.mongo.get_all_feeds()
        today = datetime.datetime.now()
        inactives = []
        for feed in feeds:
            more_recent_article = self.mongo.get_articles(feed["feed_id"], limit=1)
            last_post = next(more_recent_article)["article_date"]
            elapsed = today - last_post
            if elapsed > datetime.timedelta(days=int(nb_days)):
                inactives.append((feed, elapsed))
        tmpl = lookup.get_template("inactives.html")
        return tmpl.render(inactives=inactives, nb_days=int(nb_days))

    inactives.exposed = True

    @require()
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
            return self.error("Impossible to find a feed at this URL.")
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

    @require()
    def remove_feed(self, feed_id):
        """
        Remove a feed from the file feed.lst and from the MongoDB database.
        """
        feed = self.mongo.get_feed(feed_id)
        self.mongo.delete_feed(feed_id)
        utils.remove_feed(feed["feed_link"])
        message = """All articles from the feed <i>%s</i> are now removed from the base.""" % (feed["feed_title"],)
        tmpl = lookup.get_template("confirmation.html")
        return tmpl.render(message=message)

    remove_feed.exposed = True

    @require()
    def change_feed_url(self, feed_id, old_feed_url, new_feed_url):
        """
        Enables to change the URL of a feed already present in the database.
        """
        self.mongo.update_feed(feed_id, {"feed_link":new_feed_url})
        utils.change_feed_url(old_feed_url, new_feed_url)
        tmpl = lookup.get_template("confirmation.html")
        return tmpl.render(message="The URL of the feed has been changed.")

    change_feed_url.exposed = True

    @require()
    def change_feed_name(self, feed_id, new_feed_name):
        """
        Enables to change the name of a feed.
        """
        self.mongo.update_feed(feed_id, {"feed_title":new_feed_name})
        tmpl = lookup.get_template("confirmation.html")
        return tmpl.render(message="The name of the feed has been changed.")

    change_feed_name.exposed = True

    @require()
    def change_feed_logo(self, feed_id, new_feed_logo):
        """
        Enables to change the name of a feed.
        """
        self.mongo.update_feed(feed_id, {"feed_image":new_feed_logo})
        tmpl = lookup.get_template("confirmation.html")
        return tmpl.render(message="The logo of the feed has been changed.")

    change_feed_logo.exposed = True

    @require()
    def delete_article(self, param):
        """
        Delete an article.
        """
        try:
            feed_id, article_id = param.split(':')
            self.mongo.delete_article(feed_id, article_id)
        except:
            return self.error("Bad URL. This article do not exists.")

        return self.index()

    delete_article.exposed = True

    @require()
    def drop_base(self):
        """
        Delete all articles.
        """
        self.mongo.drop_database()
        return self.index()

    drop_base.exposed = True

    @require()
    def export(self, export_method):
        """
        Export articles currently loaded from the MongoDB database with
        the appropriate function of the 'export' module.
        """
        getattr(export, export_method)(self.mongo)
        try:
            getattr(export, export_method)(self.mongo)
        except Exception as e:
            print(e)
            return self.error(e)
        return self.management()

    export.exposed = True

    @require()
    def epub(self, param):
        """
        Export an article to EPUB.
        """
        try:
            from epub import ez_epub
        except Exception as e:
            return self.error(e)
        try:
            feed_id, article_id = param.split(':')
        except:
            return self.error("Bad URL.")
        try:
            feed_id, article_id = param.split(':')
            feed = self.mongo.get_feed(feed_id)
            articles = self.mongo.get_articles(feed_id)
            article = self.mongo.get_articles(feed_id, article_id)
        except:
            self.error("This article do not exists.")
        try:
            folder = conf.path + "/var/export/epub/"
            os.makedirs(folder)
        except OSError:
            # directories already exists (not a problem)
            pass
        section = ez_epub.Section()
        section.title = article["article_title"].decode('utf-8')
        section.paragraphs = [utils.clear_string(article["article_content"])]
        ez_epub.makeBook(article["article_title"], [feed["feed_title"]], [section], \
                os.path.normpath(folder) + "article.epub", lang='en-US', cover=None)
        return self.article(param)

    epub.exposed = True


if __name__ == '__main__':
    # Point of entry in execution mode
    root = pyAggr3g470r()
    root.favicon_ico = cherrypy.tools.staticfile.handler(filename=os.path.join(conf.path + "/img/favicon.png"))
    cherrypy.config.update({'error_page.404': error_404})
    cherrypy.quickstart(root, "/" ,config=conf.path + "/cfg/cherrypy.cfg")

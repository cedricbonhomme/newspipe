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
__version__ = "$Revision: 3.8 $"
__date__ = "$Date: 2010/01/29 $"
__revision__ = "$Date: 2013/03/15 $"
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
# - feed summary;
# - inactives;
# - languages.
# Templates are described in ./templates with the Mako
# template library.
#

import os
import re
import datetime

from collections import defaultdict

import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['static/templates'])

import conf
import utils
import export
import mongodb
import feedgetter
import auth
#from qrcode.pyqrnative.PyQRNative import QRCode, QRErrorCorrectLevel, CodeOverflowException
#from qrcode import qr


def error_404(status, message, traceback, version):
    """
    Display an error if the page does not exist.
    """
    message = "<p>Error %s - This page does not exist.</p>" % status
    tmpl = lookup.get_template("error.html")
    return tmpl.render(message=message)

def handle_error():
    """
    Handle different type of errors.
    """
    message = "<p>Sorry, an error occured.</p>"
    cherrypy.response.status = 500
    cherrypy.response.body = [message]

class RestrictedArea(object):
    """
    All methods in this controller (and subcontrollers) is
    open only to members of the admin group
    """
    _cp_config = {
        'auth.auth.require': [auth.member_of('admin')]
    }

    @cherrypy.expose
    def index(self):
        message = "<p>This is the admin only area.</p>"
        tmpl = lookup.get_template("error.html")
        return tmpl.render(message=message)

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
        self.auth = auth.AuthController()
        restricted = RestrictedArea()

        self.mongo = mongodb.Articles(conf.MONGODB_ADDRESS, conf.MONGODB_PORT, \
                        conf.MONGODB_DBNAME, conf.MONGODB_USER, conf.MONGODB_PASSWORD)
    @auth.require()
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

    @auth.require()
    def management(self):
        """
        Management page.
        Allows adding and deleting feeds. Export functions of the MongoDB data base
        and display some statistics.
        """
        feeds = self.mongo.get_all_feeds()
        nb_mail_notifications = self.mongo.nb_mail_notifications()
        nb_favorites = self.mongo.nb_favorites()
        nb_articles = format(self.mongo.nb_articles(), ",d")
        nb_unread_articles = format(self.mongo.nb_unread_articles(), ",d")
        tmpl = lookup.get_template("management.html")
        return tmpl.render(feeds=feeds, nb_mail_notifications=nb_mail_notifications, \
                            nb_favorites=nb_favorites, nb_articles=nb_articles, \
                            nb_unread_articles=nb_unread_articles, \
                            mail_notification_enabled=conf.MAIL_ENABLED)

    management.exposed = True

    @auth.require()
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

    @auth.require()
    def search(self, query=None):
        """
        Simply search for the string 'query'
        in the description of the article.
        """
        param, _, value = query.partition(':')
        feed_id = None
        if param == "Feed":
            feed_id, _, query = value.partition(':')
        search_result = self.mongo.full_search(param)
        tmpl = lookup.get_template("search.html")
        return tmpl.render(search_result=search_result, query=query, feed_id=feed_id, mongo=self.mongo)

    search.exposed = True

    @auth.require()
    def fetch(self, param=None):
        """
        Fetch all feeds.
        """
        feed_link = None
        if None != param:
            # Fetch only the feed specified in parameter
            feed_link = self.mongo.get_feed(param)["feed_link"]
        feed_getter = feedgetter.FeedGetter()
        feed_getter.retrieve_feed(feed_url=feed_link)
        return self.index()

    fetch.exposed = True

    @auth.require()
    def article(self, param, plain_text=0):
        """
        Display the article in parameter in a new Web page.
        """
        try:
            feed_id, article_id = param.split(':')
            feed = self.mongo.get_feed(feed_id)
            articles = self.mongo.get_articles(feed_id)
            article = self.mongo.get_articles(feed_id, article_id)
        except:
            return self.error("<p>Bad URL. This article do not exists.</p>")

        if article["article_readed"] == False:
            # if the current article is not yet readed, update the database
            self.mark_as_read("Article:"+article["article_id"]+":"+feed["feed_id"])

        # Description (full content) of the article
        if plain_text == "1":
            description = utils.clear_string(article["article_content"])
        else:
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
                            diaspora=conf.DIASPORA_POD, feed=feed, description=description, plain_text=plain_text)

    article.exposed = True

    @auth.require()
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
            favorites = self.mongo.get_favorites(feed_id)
            nb_favorites = self.mongo.nb_favorites(feed_id)
        except KeyError:
            return self.error("<p>This feed do not exists.</p>")

        if articles != []:
            today = datetime.datetime.now()
            last_article = articles[0]["article_date"]
            first_article = articles[self.mongo.nb_articles(feed_id)-2]["article_date"]
            delta = last_article - first_article
            elapsed = today - last_article
            average = round(nb_articles_feed / abs(delta.days), 2)

            top_words = utils.top_words(articles = self.mongo.get_articles(feed_id), n=50, size=int(word_size))
            tag_cloud = utils.tag_cloud(top_words)

        tmpl = lookup.get_template("feed.html")
        return tmpl.render(feed=feed, articles=articles, favorites=favorites, \
                            nb_articles_feed=nb_articles_feed, nb_articles_total=nb_articles_total, nb_unread_articles_feed=nb_unread_articles_feed, \
                            nb_favorites = nb_favorites, first_post_date=first_article, end_post_date=last_article, \
                            average=average, delta=delta, elapsed=elapsed, \
                            tag_cloud=tag_cloud, word_size=word_size, \
                            mail_to=conf.mail_to, mail_notification_enabled=conf.MAIL_ENABLED)

    feed.exposed = True

    @auth.require()
    def articles(self, feed_id):
        """
        This page displays all articles of a feed.
        """
        try:
            feed = self.mongo.get_feed(feed_id)
            articles = self.mongo.get_articles(feed_id)
        except KeyError:
            return self.error("<p>This feed do not exists.</p>")
        tmpl = lookup.get_template("articles.html")
        return tmpl.render(articles=articles, feed=feed)

    articles.exposed = True

    @auth.require()
    def unread(self, feed_id=""):
        """
        This page displays all unread articles of a feed.
        """
        feeds = self.mongo.get_all_feeds()
        tmpl = lookup.get_template("unread.html")
        return tmpl.render(feeds=feeds, feed_id=feed_id, mongo=self.mongo)
    unread.exposed = True

    @auth.require()
    def history(self, query="all", m=""):
        """
        This page enables to browse articles chronologically.
        """
        feeds = self.mongo.get_all_feeds()
        tmpl = lookup.get_template("history.html")
        return tmpl.render(feeds=feeds, mongo=self.mongo, query=query, m=m)

    history.exposed = True

    @auth.require()
    def error(self, message):
        """
        Display a message (bad feed id, bad article id, etc.)
        """
        tmpl = lookup.get_template("error.html")
        return tmpl.render(message=message)

    error.exposed = True

    @auth.require()
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

    @auth.require()
    def notifications(self):
        """
        List all active e-mail notifications.
        """
        feeds = self.mongo.get_all_feeds(condition=("mail",True))
        tmpl = lookup.get_template("notifications.html")
        return tmpl.render(feeds=feeds, mail_to=conf.mail_to, mail_notification_enabled=conf.MAIL_ENABLED)

    notifications.exposed = True

    @auth.require()
    def mail_notification(self, param):
        """
        Enable or disable to notifications of news for a feed.
        """
        try:
            action, feed_id = param.split(':')
        except:
            return self.error("<p>Bad URL. This feed do not exists.</p>")
        return self.index()

    mail_notification.exposed = True

    @auth.require()
    def like(self, param):
        """
        Mark or unmark an article as favorites.
        """
        try:
            like, feed_id, article_id = param.split(':')
            articles = self.mongo.get_articles(feed_id, article_id)
        except:
            return self.error("<p>Bad URL. This article do not exists.</p>")
        self.mongo.like_article("1"==like, feed_id, article_id)
        return self.article(feed_id+":"+article_id)

    like.exposed = True

    @auth.require()
    def subscriptions(self):
        """
        List all active e-mail notifications.
        """
        feeds = self.mongo.get_all_feeds()
        tmpl = lookup.get_template("subscriptions.html")
        return tmpl.render(feeds=feeds)

    subscriptions.exposed = True

    @auth.require()
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

    @auth.require()
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

    @auth.require()
    def languages(self):
        """
        Filter by languages.
        """
        try:
            from guess_language import guess_language_name
        except:
            tmpl = lookup.get_template("error.html")
            return tmpl.render(message='<p>Module <i><a href="https://bitbucket.org/spirit/guess_language/">guess_language</a></i> not installed.</p>')
        result = {}
        feeds = self.mongo.get_all_feeds()
        for feed in feeds:
            for article in self.mongo.get_articles(feed["feed_id"]):
                language = guess_language_name(utils.clear_string(article["article_content"]))
                result.setdefault(language, defaultdict(list))
                result[language][feed["feed_id"]].append(article)
        tmpl = lookup.get_template("languages.html")
        return tmpl.render(articles_sorted_by_languages=result, mongo=self.mongo)

    languages.exposed = True

    @auth.require()
    def add_feed(self, url):
        """
        Add a new feed with the URL of a page.
        """
        # search the feed in the HTML page with BeautifulSoup
        feed_url = utils.search_feed(url)
        if feed_url is None:
            return self.error("<p>Impossible to find a feed at this URL.</p>")
        # if a feed exists
        else:
            result = utils.add_feed(feed_url)
        # if the feed is not in the file feed.lst
        if result is False:
            message =  "<p>You are already following this feed!</p>"
        else:
            message = """<p>Feed added. You can now <a href="/fetch/">fetch your feeds</a>.</p>"""
        tmpl = lookup.get_template("confirmation.html")
        return tmpl.render(message=message)

    add_feed.exposed = True

    @auth.require()
    def remove_feed(self, feed_id):
        """
        Remove a feed from the file feed.lst and from the MongoDB database.
        """
        feed = self.mongo.get_feed(feed_id)
        self.mongo.delete_feed(feed_id)
        utils.remove_feed(feed["feed_link"])
        message = """<p>All articles from the feed <i>%s</i> are now removed from the base.</p>""" % (feed["feed_title"],)
        tmpl = lookup.get_template("confirmation.html")
        return tmpl.render(message=message)

    remove_feed.exposed = True

    @auth.require()
    def change_site_url(self, feed_id, old_site_url, new_site_url):
        """
        Enables to change the URL of a site present in the database.
        """
        try:
            self.mongo.update_feed(feed_id, {"site_link":new_site_url})
            tmpl = lookup.get_template("confirmation.html")
            return tmpl.render(message="<p>The URL of the site has been changed.</p>")
        except:
            return self.error("<p>Error when changing the URL of the site.</p>")

    change_site_url.exposed = True

    @auth.require()
    def change_feed_url(self, feed_id, old_feed_url, new_feed_url):
        """
        Enables to change the URL of a feed already present in the database.
        """
        self.mongo.update_feed(feed_id, {"feed_link":new_feed_url})
        result = utils.change_feed_url(old_feed_url, new_feed_url)
        if result:
            tmpl = lookup.get_template("confirmation.html")
            return tmpl.render(message="<p>The URL of the feed has been changed.</p>")
        else:
            return self.error("<p>Error when changing the URL of the feed.</p>")

    change_feed_url.exposed = True

    @auth.require()
    def change_feed_name(self, feed_id, new_feed_name):
        """
        Enables to change the name of a feed.
        """
        try:
            self.mongo.update_feed(feed_id, {"feed_title":new_feed_name})
            tmpl = lookup.get_template("confirmation.html")
            return tmpl.render(message="<p>The name of the feed has been changed.</p>")
        except:
            return self.error("<p>Error when changing the name of the feed.</p>")

    change_feed_name.exposed = True

    @auth.require()
    def change_feed_logo(self, feed_id, new_feed_logo):
        """
        Enables to change the name of a feed.
        """
        try:
            self.mongo.update_feed(feed_id, {"feed_image":new_feed_logo})
            tmpl = lookup.get_template("confirmation.html")
            return tmpl.render(message="<p>The logo of the feed has been changed.</p>")
        except:
            return self.error("<p>Error when changing the logo of the feed.</p>")

    change_feed_logo.exposed = True

    @auth.require()
    def change_username(self, new_username):
        """
        Enables to change the username of a user.
        """
        result = auth.change_username(self.auth.username, new_username)
        if result:
            self.auth.username = new_username
            tmpl = lookup.get_template("confirmation.html")
            return tmpl.render(message="<p>Your username has been changed.</p>")
        else:
            return self.error("<p>Impossible to change the username.</p>")

    change_username.exposed = True

    @auth.require()
    def change_password(self, new_password):
        """
        Enables to change the password of a user.
        """
        result = auth.change_password(self.auth.username, new_password)
        if result:
            tmpl = lookup.get_template("confirmation.html")
            return tmpl.render(message="<p>Your password has been changed.</p>")
        else:
            return self.error("<p>Impossible to change the password.</p>")

    change_password.exposed = True

    @auth.require()
    def delete_article(self, param):
        """
        Delete an article.
        """
        try:
            feed_id, article_id = param.split(':')
            self.mongo.delete_article(feed_id, article_id)
        except:
            return self.error("<p>Bad URL. This article do not exists.</p>")

        return self.index()

    delete_article.exposed = True

    @auth.require()
    def logout(self):
        """
        Close the session.
        """
        return self.auth.logout()

    logout.exposed = True


    @auth.require()
    def drop_base(self):
        """
        Delete all articles.
        """
        self.mongo.drop_database()
        return self.index()

    drop_base.exposed = True

    @auth.require()
    def export(self, export_method):
        """
        Export articles currently loaded from the MongoDB database with
        the appropriate function of the 'export' module.
        """
        getattr(export, export_method)(self.mongo)
        try:
            getattr(export, export_method)(self.mongo)
        except Exception as e:
            return self.error(e)
        tmpl = lookup.get_template("confirmation.html")
        return tmpl.render(message="<p>Export successfully terminated.<br />Check the folder: <b>" + conf.path + "/var/export/</b>.</p>")

    export.exposed = True

    @auth.require()
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
            self.error("<p>This article do not exists.</p>")
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
    root.favicon_ico = cherrypy.tools.staticfile.handler(filename=os.path.join(conf.path + "/static/img/favicon.png"))
    cherrypy.config.update({'error_page.404': error_404})
    cherrypy.quickstart(root, "/" ,config=conf.path + "/cfg/cherrypy.cfg")

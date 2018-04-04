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
__version__ = "$Revision: 0.2 $"
__date__ = "$Date: 2016/11/17 $"
__revision__ = "$Date: 2017/05/14 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "AGPLv3"

#
# This file contains the import/export functions of Newspipe.
#

import json
import opml
import datetime
from flask import jsonify

from bootstrap import db
from web.models import User, Feed, Article
from web.models.tag import BookmarkTag
from web.controllers import BookmarkController, BookmarkTagController


def import_opml(nickname, opml_content):
    """
    Import new feeds from an OPML file.
    """
    user = User.query.filter(User.nickname == nickname).first()
    try:
        subscriptions = opml.from_string(opml_content)
    except:
        logger.exception("Parsing OPML file failed:")
        raise

    def read(subsubscription, nb=0):
        """
        Parse recursively through the categories and sub-categories.
        """
        for subscription in subsubscription:
            if len(subscription) != 0:
                nb = read(subscription, nb)
            else:
                try:
                    title = subscription.text
                except:
                    title = ""
                try:
                    description = subscription.description
                except:
                    description = ""
                try:
                    link = subscription.xmlUrl
                except:
                    continue
                if None != Feed.query.filter(Feed.user_id == user.id, Feed.link == link).first():
                    continue
                try:
                    site_link = subscription.htmlUrl
                except:
                    site_link = ""
                new_feed = Feed(title=title, description=description,
                                link=link, site_link=site_link,
                                enabled=True)
                user.feeds.append(new_feed)
                nb += 1
        return nb
    nb = read(subscriptions)
    db.session.commit()
    return nb


def import_json(nickname, json_content):
    """
    Import an account from a JSON file.
    """
    user = User.query.filter(User.nickname == nickname).first()
    json_account = json.loads(json_content.decode("utf-8"))
    nb_feeds, nb_articles = 0, 0
    # Create feeds:
    for feed in json_account:
        if None != Feed.query.filter(Feed.user_id == user.id,
                                    Feed.link == feed["link"]).first():
            continue
        new_feed = Feed(title=feed["title"],
                        description="",
                        link=feed["link"],
                        site_link=feed["site_link"],
                        created_date=datetime.datetime.
                            fromtimestamp(int(feed["created_date"])),
                        enabled=feed["enabled"])
        user.feeds.append(new_feed)
        nb_feeds += 1
    db.session.commit()
    # Create articles:
    for feed in json_account:
        user_feed = Feed.query.filter(Feed.user_id == user.id,
                                        Feed.link == feed["link"]).first()
        if None != user_feed:
            for article in feed["articles"]:
                if None == Article.query.filter(Article.user_id == user.id,
                                    Article.feed_id == user_feed.id,
                                    Article.link == article["link"]).first():
                    new_article = Article(entry_id=article["link"],
                                link=article["link"],
                                title=article["title"],
                                content=article["content"],
                                readed=article["readed"],
                                like=article["like"],
                                retrieved_date=datetime.datetime.
                                    fromtimestamp(int(article["retrieved_date"])),
                                date=datetime.datetime.
                                    fromtimestamp(int(article["date"])),
                                user_id=user.id,
                                feed_id=user_feed.id)
                    user_feed.articles.append(new_article)
                    nb_articles += 1
    db.session.commit()
    return nb_feeds, nb_articles


def export_json(user):
    """
    Export all articles of user in JSON.
    """
    articles = []
    for feed in user.feeds:
        articles.append({
            "title": feed.title,
            "description": feed.description,
            "link": feed.link,
            "site_link": feed.site_link,
            "enabled": feed.enabled,
            "created_date": feed.created_date.strftime('%s'),
            "articles": [ {
                "title": article.title,
                "link": article.link,
                "content": article.content,
                "readed": article.readed,
                "like": article.like,
                "date": article.date.strftime('%s'),
                "retrieved_date": article.retrieved_date.strftime('%s')
                                                } for article in feed.articles]
        })
    return jsonify(articles)


def import_pinboard_json(user, json_content):
    """Import bookmarks from a pinboard JSON export.
    """
    bookmark_contr = BookmarkController(user.id)
    tag_contr = BookmarkTagController(user.id)
    bookmarks = json.loads(json_content.decode("utf-8"))
    nb_bookmarks = 0
    for bookmark in bookmarks:
        tags = []
        for tag in bookmark['tags'].split(' '):
            new_tag = BookmarkTag(text=tag.strip(), user_id=user.id)
            tags.append(new_tag)
        bookmark_attr = {
                    'href': bookmark['href'],
                    'description': bookmark['extended'],
                    'title': bookmark['description'],
                    'shared': [bookmark['shared']=='yes' and True or False][0],
                    'to_read': [bookmark['toread']=='yes' and True or False][0],
                    'time': datetime.datetime.strptime(bookmark['time'],
                                                        '%Y-%m-%dT%H:%M:%SZ'),
                    'tags': tags
                    }
        new_bookmark = bookmark_contr.create(**bookmark_attr)
        nb_bookmarks += 1
    return nb_bookmarks


def export_bookmarks(user):
    """Export all bookmarks of a user (compatible with Pinboard).
    """
    bookmark_contr = BookmarkController(user.id)
    bookmarks = bookmark_contr.read()
    export = []
    for bookmark in bookmarks:
        export.append({
            'href': bookmark.href,
            'description': bookmark.description,
            'title': bookmark.title,
            'shared': 'yes' if bookmark.shared else 'no',
            'toread': 'yes' if bookmark.to_read else 'no',
            'time': bookmark.time.isoformat(),
            'tags': ' '.join(bookmark.tags_proxy)
        })
    return jsonify(export)

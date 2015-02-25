#! /usr/bin/env python
# -*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2015  Cédric Bonhomme - http://cedricbonhomme.org/
#
# For more information : https://bitbucket.org/cedricbonhomme/pyaggr3g470r/
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
__date__ = "$Date: 2014/06/18 $"
__revision__ = "$Date: 2014/07/05 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "AGPLv3"

import re
import dateutil.parser
from functools import wraps
from flask import g, Response, request, session, jsonify
from flask.ext.restful import Resource, reqparse

import conf
if not conf.ON_HEROKU:
    import pyaggr3g470r.search as fastsearch
from pyaggr3g470r import api, db
from pyaggr3g470r.models import User, Article, Feed

def authenticate(func):
    """
    Decorator for the authentication to the web services.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not getattr(func, 'authenticated', True):
            return func(*args, **kwargs)

        # authentication based on the session (already logged on the site)
        if 'email' in session or g.user.is_authenticated():
            return func(*args, **kwargs)

        # authentication via HTTP only
        auth = request.authorization
        try:
            email = auth.username
            user = User.query.filter(User.email == email).first()
            if user and user.check_password(auth.password) and user.activation_key == "":
                g.user = user
                return func(*args, **kwargs)
        except AttributeError:
            pass

        return Response('<Authentication required>', 401,
                        {'WWWAuthenticate':'Basic realm="Login Required"'})
    return wrapper

class ArticleListAPI(Resource):
    """
    Defines a RESTful API for Article elements.
    """
    method_decorators = [authenticate]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = unicode, location = 'json')
        self.reqparse.add_argument('content', type = unicode, location = 'json')
        self.reqparse.add_argument('link', type = unicode, location = 'json')
        self.reqparse.add_argument('date', type = str, location = 'json')
        self.reqparse.add_argument('feed_id', type = int, location = 'json')
        super(ArticleListAPI, self).__init__()

    def get(self):
        """
        Returns a list of articles.
        """
        feeds = {feed.id: feed.title for feed in g.user.feeds if feed.enabled}
        articles = Article.query.filter(Article.feed_id.in_(feeds.keys()), 
                                        Article.user_id == g.user.id)
        filter_ = request.args.get('filter_', 'unread')
        feed_id = int(request.args.get('feed', 0))
        limit = request.args.get('limit', 1000)
        if filter_ != 'all':
            articles = articles.filter(Article.readed == (filter_ == 'read'))
        if feed_id:
            articles = articles.filter(Article.feed_id == feed_id)

        articles = articles.order_by(Article.date.desc())
        if limit != 'all':
            limit = int(limit)
            articles = articles.limit(limit)

        return jsonify(result= [{
                                    "id": article.id,
                                    "title": article.title,
                                    "link": article.link,
                                    "content": article.content,
                                    "readed": article.readed,
                                    "like": article.like,
                                    "date": article.date,
                                    "retrieved_date": article.retrieved_date,
                                    "feed_id": article.source.id,
                                    "feed_name": article.source.title
                                }
                                for article in articles]
                        )

    def post(self):
        """
        POST method - Create a new article.
        """
        args = self.reqparse.parse_args()
        article_dict = {}
        for k, v in args.iteritems():
            if v != None:
                article_dict[k] = v
            else:
                return {"message":"Missing argument: %s." % (k,)}
        article_date = None
        try:
            article_date = dateutil.parser.parse(article_dict["date"], dayfirst=True)
        except:
            try:  # trying to clean date field from letters
                article_date = dateutil.parser.parse(re.sub('[A-z]', '', article_dict["date"], dayfirst=True))
            except:
                return jsonify({"message":"Bad format for the date."})
        article = Article(link=article_dict["link"], title=article_dict["title"],
                                content=article_dict["content"], readed=False, like=False,
                                date=article_date, user_id=g.user.id,
                                feed_id=article_dict["feed_id"])
        feed = Feed.query.filter(Feed.id == article_dict["feed_id"], Feed.user_id == g.user.id).first()
        feed.articles.append(article)
        try:
            db.session.commit()
            return jsonify({"message":"ok"})
        except:
            return jsonify({"message":"Impossible to create the article."})

class ArticleAPI(Resource):
    """
    Defines a RESTful API for Article elements.
    """
    method_decorators = [authenticate]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('like', type = bool, location = 'json')
        self.reqparse.add_argument('readed', type = bool, location = 'json')
        super(ArticleAPI, self).__init__()

    def get(self, id=None):
        """
        Returns an article.
        """
        result = []
        if id is not None:
            article = Article.query.filter(Article.user_id == g.user.id, Article.id == id).first()
            if article is not None:
                if not article.readed:
                    article.readed = True
                    db.session.commit()
                result.append(article)

        return jsonify(result= [{
                                    "id": article.id,
                                    "title": article.title,
                                    "link": article.link,
                                    "content": article.content,
                                    "readed": article.readed,
                                    "like": article.like,
                                    "date": article.date,
                                    "retrieved_date": article.retrieved_date,
                                    "feed_id": article.source.id,
                                    "feed_name": article.source.title
                                }
                                for article in result]
                        )

    def put(self, id):
        """
        Update an article.
        It is only possible to update the status ('like' and 'readed') of an article.
        """
        args = self.reqparse.parse_args()
        article = Article.query.filter(Article.id == id).first()
        if article is not None and article.source.subscriber.id == g.user.id:
            if None is not args.get('like', None):
                article.like = args['like']
            if None is not args.get('readed', None):
                article.readed = args['readed']
            db.session.commit()

            try:
                fastsearch.delete_article(g.user.id, article.feed_id, article.id)
            except:
                pass

            return jsonify({"message":"ok"})
        else:
            return jsonify({'message': 'Article not found.'})

    def delete(self, id):
        """
        Delete an article.
        """
        article = Article.query.filter(Article.id == id).first()
        if article is not None and article.source.subscriber.id == g.user.id:
            db.session.delete(article)
            db.session.commit()
            return jsonify({"message":"ok"})
        else:
            return jsonify({'message': 'Article not found.'})

api.add_resource(ArticleListAPI, '/api/v1.0/articles', endpoint = 'articles.json')
api.add_resource(ArticleAPI, '/api/v1.0/articles/<int:id>', endpoint = 'article.json')

class FeedListAPI(Resource):
    """
    Defines a RESTful API for Feed elements.
    """
    method_decorators = [authenticate]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = unicode, default = "", location = 'json')
        self.reqparse.add_argument('description', type = unicode, default = "", location = 'json')
        self.reqparse.add_argument('link', type = unicode, location = 'json')
        self.reqparse.add_argument('site_link', type = unicode, default = "", location = 'json')
        self.reqparse.add_argument('enabled', type = bool, default = True ,location = 'json')
        super(FeedListAPI, self).__init__()

    def get(self):
        """
        Returns a list of feeds.
        """
        return jsonify(result= [{
                                    "id": feed.id,
                                    "title": feed.title,
                                    "description": feed.description,
                                    "link": feed.link,
                                    "site_link": feed.site_link,
                                    "enabled": feed.enabled,
                                    "created_date": feed.created_date
                                }
                                for feed in g.user.feeds]
                        )

    def post(self):
        """
        POST method - Create a new feed.
        """
        args = self.reqparse.parse_args()
        feed_dict = {}
        for k, v in args.iteritems():
            if v != None:
                feed_dict[k] = v
            else:
                return jsonify({'message': 'missing argument: %s' % (k,)})
        new_feed = Feed(title=feed_dict["title"], description=feed_dict["description"],
                        link=feed_dict["link"], site_link=feed_dict["site_link"],
                        enabled=feed_dict["enabled"])
        g.user.feeds.append(new_feed)
        try:
            db.session.commit()
            return jsonify({"message":"ok"})
        except:
            return jsonify({'message': 'Impossible to create the feed.'})

class FeedAPI(Resource):
    """
    Defines a RESTful API for Feed elements.
    """
    method_decorators = [authenticate]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = unicode, location = 'json')
        self.reqparse.add_argument('description', type = unicode, location = 'json')
        self.reqparse.add_argument('link', type = unicode, location = 'json')
        self.reqparse.add_argument('site_link', type = unicode, location = 'json')
        self.reqparse.add_argument('enabled', type = bool ,location = 'json')
        super(FeedAPI, self).__init__()

    def get(self, id=None):
        """
        Returns a feed.
        """
        result = []
        if id is not None:
            feed = Feed.query.filter(Feed.id == id, Feed.user_id == g.user.id).first()
            if feed is not None:
                result.append(feed)
                return jsonify(result= [{
                                            "id": feed.id,
                                            "title": feed.title,
                                            "description": feed.description,
                                            "link": feed.link,
                                            "site_link": feed.site_link,
                                            "nb_articles": feed.articles.count()
                                        }
                                        for feed in result]
                                )
        return jsonify({'message': 'Feed not found'})

    def put(self, id):
        """
        Update a feed.
        """
        args = self.reqparse.parse_args()
        feed = Feed.query.filter(Feed.id == id, Feed.user_id == g.user.id).first()
        if feed is not None:
            if None is not args.get('title', None):
                feed.title = args['title']
            if None is not args.get('description', None):
                feed.description = args['description']
            if None is not args.get('link', None):
                feed.link = args['link']
            if None is not args.get('site_link', None):
                feed.site_link = args['site_link']
            if None is not args.get('enabled', None):
                feed.enabled = args['enabled']
            db.session.commit()
            return jsonify({"message":"ok"})
        else:
            return jsonify({'message': 'Feed not found.'})

    def delete(self, id):
        """
        Delete a feed.
        """
        feed = Feed.query.filter(Feed.id == id, Feed.user_id == g.user.id).first()
        if feed is not None:
            db.session.delete(feed)
            db.session.commit()
            return jsonify({"message":"ok"})
        else:
            return jsonify({'message': 'Feed not found.'})

api.add_resource(FeedListAPI, '/api/v1.0/feeds', endpoint = 'feeds.json')
api.add_resource(FeedAPI, '/api/v1.0/feeds/<int:id>', endpoint = 'feed.json')
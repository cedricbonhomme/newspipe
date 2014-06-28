#! /usr/bin/env python
# -*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2014  Cédric Bonhomme - http://cedricbonhomme.org/
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
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2014/06/18 $"
__revision__ = "$Date: 2014/06/18 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "AGPLv3"

import re
import dateutil.parser
from functools import wraps
from flask import g, Response, request, session, jsonify
from flask.ext.restful import Resource, reqparse
#from flask.ext.restful.inputs import boolean

if not conf.ON_HEROKU:
    import search as fastsearch
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
                return {"message":"missing argument: %s" % (k,)}
        article_date = None
        try:
            article_date = dateutil.parser.parse(article_dict["date"], dayfirst=True)
        except:
            try:  # trying to clean date field from letters
                article_date = dateutil.parser.parse(re.sub('[A-z]', '', article_dict["date"], dayfirst=True))
            except:
                return {"message":"bad format for the date"}
        article = Article(link=article_dict["link"], title=article_dict["title"],
                                content=article_dict["content"], readed=False, like=False,
                                date=article_date, user_id=g.user.id,
                                feed_id=article_dict["feed_id"])
        feed = Feed.query.filter(Feed.id == article_dict["feed_id"], Feed.user_id == g.user.id).first()
        feed.articles.append(article)
        db.session.commit()
        return {"message":"ok"}

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

            return {"message":"ok"}
        else:
            response = jsonify({'code': 404, 'message': 'Article not found'})
            response.status_code = 404
            return response

    def delete(self, id):
        """
        Delete an article.
        """
        article = Article.query.filter(Article.id == id).first()
        if article is not None and article.source.subscriber.id == g.user.id:
            db.session.delete(article)
            db.session.commit()
            return {"message":"ok"}
        else:
            response = jsonify({'code': 404, 'message': 'Article not found'})
            response.status_code = 404
            return response

api.add_resource(ArticleListAPI, '/api/v1.0/articles', endpoint = 'articles.json')
api.add_resource(ArticleAPI, '/api/v1.0/articles/<int:id>', endpoint = 'article.json')

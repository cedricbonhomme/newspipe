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

from functools import wraps
from flask import g, Response, request, session, jsonify
from flask.ext.restful import Resource, reqparse

from pyaggr3g470r import api, db
from pyaggr3g470r.models import User, Article

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
        #self.reqparse = reqparse.RequestParser()
        #self.reqparse.add_argument('item_id', type = str, location = 'json')
        #self.reqparse.add_argument('item_title', type = unicode, location = 'json')
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
        pass

    def put(self):
        pass

    def delete(self):
        pass

class ArticleAPI(Resource):
    """
    Defines a RESTful API for Article elements.
    """
    method_decorators = [authenticate]

    def __init__(self):
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

    def post(self, id):
        """
        Update an article.
        """
        pass

    def put(self, id):
        """
        Create an article.
        """
        pass

    def delete(self, id):
        """
        Delete an article.
        """
        pass

api.add_resource(ArticleListAPI, '/api/v1.0/articles', endpoint = 'articles.json')
api.add_resource(ArticleAPI, '/api/v1.0/articles/<int:id>', endpoint = 'article.json')

import re
import dateutil.parser

import conf
if not conf.ON_HEROKU:
    import pyaggr3g470r.search as fastsearch

from flask import request, g
from flask.ext.restful import Resource, reqparse

from pyaggr3g470r import api, db
from pyaggr3g470r.models import Article, Feed
from pyaggr3g470r.views.api.common import authenticate, to_response, \
                                          PyAggResource


class ArticleListAPI(Resource):
    """
    Defines a RESTful API for Article elements.
    """
    method_decorators = [authenticate, to_response]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=unicode, location='json')
        self.reqparse.add_argument('content', type=unicode, location='json')
        self.reqparse.add_argument('link', type=unicode, location='json')
        self.reqparse.add_argument('date', type=str, location='json')
        self.reqparse.add_argument('feed_id', type=int, location='json')
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

        return {'result': [article.dump() for article in articles]}

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
                return {"message": "Missing argument: %s." % (k,)}, 400
        article_date = None
        try:
            article_date = dateutil.parser.parse(article_dict["date"], dayfirst=True)
        except:
            try:  # trying to clean date field from letters
                article_date = dateutil.parser.parse(re.sub('[A-z]', '', article_dict["date"], dayfirst=True))
            except:
                return {"message": "Bad format for the date."}, 400
        article = Article(link=article_dict["link"], title=article_dict["title"],
                                content=article_dict["content"], readed=False, like=False,
                                date=article_date, user_id=g.user.id,
                                feed_id=article_dict["feed_id"])
        feed = Feed.query.filter(Feed.id == article_dict["feed_id"], Feed.user_id == g.user.id).first()
        feed.articles.append(article)
        try:
            db.session.commit()
            return {"message": "ok"}, 201
        except:
            return {"message": "Impossible to create the article."}, 500


class ArticleAPI(PyAggResource):
    "Defines a RESTful API for Article elements."
    method_decorators = [authenticate, to_response]
    db_cls = Article

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('like', type=bool, location='json')
        self.reqparse.add_argument('readed', type=bool, location= 'json')
        super(ArticleAPI, self).__init__()

    def get(self, id):
        article = self._get_or_raise(id)
        if not article.readed:
            article.readed = True
            db.session.commit()
        return {'result': [article.dump()]}

    def put(self, id):
        """ Update an article. It is only possible to update the status
        ('like' and 'readed') of an article."""
        args = self.reqparse.parse_args()
        article = self._get_or_raise(id)
        if 'like' in args:
            article.like = args['like']
        if 'readed' in args:
            article.readed = args['readed']
        db.session.commit()

        try:
            fastsearch.delete_article(g.user.id, article.feed_id, article.id)
        except:
            pass
        return {"message": "ok"}


api.add_resource(ArticleListAPI, '/api/v1.0/articles',
                 endpoint='articles.json')
api.add_resource(ArticleAPI, '/api/v1.0/articles/<int:id>',
                 endpoint='article.json')

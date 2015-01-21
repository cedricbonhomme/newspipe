from flask import g

from pyaggr3g470r.controllers import ArticleController
from pyaggr3g470r.views.api.common import PyAggResourceNew, \
                                          PyAggResourceExisting, \
                                          PyAggResourceMulti


ARTICLE_ATTRS = {'title': {'type': str},
                 'content': {'type': str},
                 'link': {'type': str},
                 'date': {'type': str},
                 'feed_id': {'type': int},
                 'like': {'type': bool},
                 'readed': {'type': bool}}


class ArticleNewAPI(PyAggResourceNew):
    controller_cls = ArticleController
    attrs = ARTICLE_ATTRS


class ArticleAPI(PyAggResourceExisting):
    controller_cls = ArticleController
    attrs = ARTICLE_ATTRS


class ArticlesAPI(PyAggResourceMulti):
    controller_cls = ArticleController
    attrs = ARTICLE_ATTRS


g.api.add_resource(ArticleNewAPI, '/article', endpoint='article_new.json')
g.api.add_resource(ArticleAPI, '/article/<int:obj_id>',
                   endpoint='article.json')
g.api.add_resource(ArticlesAPI, '/articles', endpoint='articles.json')

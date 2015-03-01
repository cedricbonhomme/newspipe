from flask import g
import dateutil.parser

from pyaggr3g470r.controllers import ArticleController
from pyaggr3g470r.views.api.common import PyAggAbstractResource,\
                                          PyAggResourceNew, \
                                          PyAggResourceExisting, \
                                          PyAggResourceMulti


ARTICLE_ATTRS = {'feed_id': {'type': str},
                 'entry_id': {'type': str},
                 'link': {'type': str},
                 'title': {'type': str},
                 'readed': {'type': bool}, 'like': {'type': bool},
                 'content': {'type': str},
                 'date': {'type': str}, 'retrieved_date': {'type': str}}


class ArticleNewAPI(PyAggResourceNew):
    controller_cls = ArticleController
    attrs = ARTICLE_ATTRS
    to_date = ['date', 'retrieved_date']


class ArticleAPI(PyAggResourceExisting):
    controller_cls = ArticleController
    attrs = ARTICLE_ATTRS
    to_date = ['date', 'retrieved_date']


class ArticlesAPI(PyAggResourceMulti):
    controller_cls = ArticleController
    attrs = ARTICLE_ATTRS
    to_date = ['date', 'retrieved_date']


class ArticlesChallenge(PyAggAbstractResource):
    controller_cls = ArticleController
    attrs = {'ids': {'type': list, 'default': []}}
    to_date = ['date', 'retrieved_date']

    def get(self):
        parsed_args = self.reqparse_args()
        for id_dict in parsed_args['ids']:
            for key in self.to_date:
                if key in id_dict:
                    id_dict[key] = dateutil.parser.parse(id_dict[key])

        return self.controller.challenge(parsed_args['ids'])


g.api.add_resource(ArticleNewAPI, '/article', endpoint='article_new.json')
g.api.add_resource(ArticleAPI, '/article/<int:obj_id>',
                   endpoint='article.json')
g.api.add_resource(ArticlesAPI, '/articles', endpoint='articles.json')
g.api.add_resource(ArticlesChallenge, '/articles/challenge',
                   endpoint='articles_challenge.json')

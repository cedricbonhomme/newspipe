from datetime import datetime

import dateutil.parser
from flask import current_app
from flask_restful import Api

from newspipe.bootstrap import application
from newspipe.controllers import ArticleController
from newspipe.web.views.api.v2.common import PyAggAbstractResource
from newspipe.web.views.api.v2.common import PyAggResourceExisting
from newspipe.web.views.api.v2.common import PyAggResourceMulti
from newspipe.web.views.api.v2.common import PyAggResourceNew
from newspipe.web.views.common import api_permission


class ArticleNewAPI(PyAggResourceNew):
    controller_cls = ArticleController


class ArticleAPI(PyAggResourceExisting):
    controller_cls = ArticleController


class ArticlesAPI(PyAggResourceMulti):
    controller_cls = ArticleController


class ArticlesChallenge(PyAggAbstractResource):
    controller_cls = ArticleController
    attrs = {"ids": {"type": list, "default": []}}

    @api_permission.require(http_exception=403)
    def get(self):
        parsed_args = self.reqparse_args(right="read")
        # collecting all attrs for casting purpose
        attrs = self.controller_cls._get_attrs_desc("admin")
        for id_dict in parsed_args["ids"]:
            keys_to_ignore = []
            for key in id_dict:
                if key not in attrs:
                    keys_to_ignore.append(key)
                if issubclass(attrs[key]["type"], datetime):
                    id_dict[key] = dateutil.parser.parse(id_dict[key])
            for key in keys_to_ignore:
                del id_dict[key]

        result = list(self.controller.challenge(parsed_args["ids"]))
        return result or None, 200 if result else 204


api = Api(current_app, prefix=application.config["API_ROOT"])

api.add_resource(ArticleNewAPI, "/article", endpoint="article_new.json")
api.add_resource(ArticleAPI, "/article/<int:obj_id>", endpoint="article.json")
api.add_resource(ArticlesAPI, "/articles", endpoint="articles.json")
api.add_resource(
    ArticlesChallenge, "/articles/challenge", endpoint="articles_challenge.json"
)

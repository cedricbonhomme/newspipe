from flask import current_app
from flask_restful import Api

from newspipe.bootstrap import application
from newspipe.bootstrap import csrf
from newspipe.controllers.feed import DEFAULT_LIMIT
from newspipe.controllers.feed import DEFAULT_MAX_ERROR
from newspipe.controllers.feed import FeedController
from newspipe.web.views.api.v2.common import PyAggAbstractResource
from newspipe.web.views.api.v2.common import PyAggResourceExisting
from newspipe.web.views.api.v2.common import PyAggResourceMulti
from newspipe.web.views.api.v2.common import PyAggResourceNew
from newspipe.web.views.common import api_permission


class FeedNewAPI(PyAggResourceNew):
    controller_cls = FeedController


class FeedAPI(PyAggResourceExisting):
    controller_cls = FeedController


class FeedsAPI(PyAggResourceMulti):
    controller_cls = FeedController


class FetchableFeedAPI(PyAggAbstractResource):
    controller_cls = FeedController
    attrs = {
        "max_error": {"type": int, "default": DEFAULT_MAX_ERROR},
        "limit": {"type": int, "default": DEFAULT_LIMIT},
    }

    @api_permission.require(http_exception=403)
    def get(self):
        args = self.reqparse_args(right="read", allow_empty=True)
        result = [feed for feed in self.controller.list_fetchable(**args)]
        return result or None, 200 if result else 204


api = Api(current_app, prefix=application.config["API_ROOT"], decorators=[csrf.exempt])

api.add_resource(FeedNewAPI, "/feed", endpoint="feed_new.json")
api.add_resource(FeedAPI, "/feed/<int:obj_id>", endpoint="feed.json")
api.add_resource(FeedsAPI, "/feeds", endpoint="feeds.json")
api.add_resource(FetchableFeedAPI, "/feeds/fetchable", endpoint="fetchable_feed.json")

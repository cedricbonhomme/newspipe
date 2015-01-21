from datetime import datetime
from flask import g
from flask.ext.restful import Resource, reqparse

from pyaggr3g470r.controllers.feed import FeedController, \
                                          DEFAULT_MAX_ERROR, DEFAULT_LIMIT

from pyaggr3g470r.views.api.common import PyAggResourceNew, \
                                          PyAggResourceExisting, \
                                          PyAggResourceMulti


FEED_ATTRS = {'title': {'type': str},
              'description': {'type': str},
              'link': {'type': str},
              'site_link': {'type': str},
              'email_notification': {'type': bool, 'default': False},
              'enabled': {'type': bool, 'default': True},
              'etag': {'type': str, 'default': None},
              'last_modified': {'type': datetime},
              'last_error': {'type': datetime},
              'error_count': {'type': int, 'default': 0}}


class FeedNewAPI(PyAggResourceNew):
    controller_cls = FeedController
    attrs = FEED_ATTRS


class FeedAPI(PyAggResourceExisting):
    pass
    controller_cls = FeedController
    attrs = FEED_ATTRS


class FeedsAPI(PyAggResourceMulti):
    pass
    controller_cls = FeedController
    attrs = FEED_ATTRS


class FetchableFeedAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('max_error', type=int, location='json',
                default=DEFAULT_MAX_ERROR)
        self.reqparse.add_argument('limit', type=int, location='json',
                default=DEFAULT_LIMIT)
        super(FetchableFeedAPI, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        controller = FeedController(g.user.id)
        return [feed for feed in controller.list_fetchable(
                            max_error=args['max_error'], limit=args['limit'])]


g.api.add_resource(FeedNewAPI, '/feed', endpoint='feed_new.json')
g.api.add_resource(FeedAPI, '/feed/<int:obj_id>', endpoint='feed.json')
g.api.add_resource(FeedsAPI, '/feeds', endpoint='feeds.json')
g.api.add_resource(FetchableFeedAPI, '/feeds/fetchable',
                   endpoint='fetchable_feed.json')

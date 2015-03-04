from flask import g

from pyaggr3g470r.controllers.feed import FeedController, \
                                          DEFAULT_MAX_ERROR, DEFAULT_LIMIT

from pyaggr3g470r.views.api.common import PyAggAbstractResource, \
                                          PyAggResourceNew, \
                                          PyAggResourceExisting, \
                                          PyAggResourceMulti


FEED_ATTRS = {'title': {'type': str},
              'description': {'type': str},
              'link': {'type': str},
              'site_link': {'type': str},
              'enabled': {'type': bool, 'default': True},
              'etag': {'type': str, 'default': ''},
              'last_modified': {'type': str},
              'last_retrieved': {'type': str},
              'last_error': {'type': str},
              'error_count': {'type': int, 'default': 0}}


class FeedNewAPI(PyAggResourceNew):
    controller_cls = FeedController
    attrs = FEED_ATTRS
    to_date = ['date', 'last_retrieved']


class FeedAPI(PyAggResourceExisting):
    controller_cls = FeedController
    attrs = FEED_ATTRS
    to_date = ['date', 'last_retrieved']


class FeedsAPI(PyAggResourceMulti):
    controller_cls = FeedController
    attrs = FEED_ATTRS
    to_date = ['date', 'last_retrieved']


class FetchableFeedAPI(PyAggAbstractResource):
    controller_cls = FeedController
    to_date = ['date', 'last_retrieved']
    attrs = {'max_error': {'type': int, 'default': DEFAULT_MAX_ERROR},
             'limit': {'type': int, 'default': DEFAULT_LIMIT}}

    def get(self):
        return [feed for feed in self.controller.list_fetchable(
                                                    **self.reqparse_args())]


g.api.add_resource(FeedNewAPI, '/feed', endpoint='feed_new.json')
g.api.add_resource(FeedAPI, '/feed/<int:obj_id>', endpoint='feed.json')
g.api.add_resource(FeedsAPI, '/feeds', endpoint='feeds.json')
g.api.add_resource(FetchableFeedAPI, '/feeds/fetchable',
                   endpoint='fetchable_feed.json')

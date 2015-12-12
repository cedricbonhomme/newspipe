#! /usr/bin/env python
# -*- coding: utf-8 -

from flask import g

from web.controllers.feed import (FeedController,
                                           DEFAULT_MAX_ERROR,
                                           DEFAULT_LIMIT,
                                           DEFAULT_REFRESH_RATE)

from web.views.api.common import PyAggAbstractResource, \
                                          PyAggResourceNew, \
                                          PyAggResourceExisting, \
                                          PyAggResourceMulti

FEED_ATTRS = {'title': {'type': str},
              'description': {'type': str},
              'link': {'type': str},
              'user_id': {'type': int},
              'site_link': {'type': str},
              'enabled': {'type': bool, 'default': True},
              'etag': {'type': str, 'default': ''},
              'icon_url': {'type': str, 'default': ''},
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
             'limit': {'type': int, 'default': DEFAULT_LIMIT},
             'refresh_rate': {'type': int, 'default': DEFAULT_REFRESH_RATE},
             'retreive_all': {'type': bool, 'default': False}}

    def get(self):
        args = self.reqparse_args()
        if g.user.refresh_rate:
            args['refresh_rate'] = g.user.refresh_rate

        if args.pop('retreive_all', False):
            contr = self.wider_controller
        else:
            contr = self.controller
        result = [feed for feed in contr.list_fetchable(**args)]
        return result or None, 200 if result else 204


g.api.add_resource(FeedNewAPI, '/feed', endpoint='feed_new.json')
g.api.add_resource(FeedAPI, '/feed/<int:obj_id>', endpoint='feed.json')
g.api.add_resource(FeedsAPI, '/feeds', endpoint='feeds.json')
g.api.add_resource(FetchableFeedAPI, '/feeds/fetchable',
                   endpoint='fetchable_feed.json')

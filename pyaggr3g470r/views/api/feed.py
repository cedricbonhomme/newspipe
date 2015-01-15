from flask import g
from flask.ext.restful import Resource, reqparse

from pyaggr3g470r import api, db
from pyaggr3g470r.models import Feed

from pyaggr3g470r.views.api.common import authenticate, to_response, \
                                          PyAggResource


class FeedListAPI(Resource):
    """
    Defines a RESTful API for Feed elements.
    """
    method_decorators = [authenticate, to_response]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title',
                                   type=unicode, default="", location='json')
        self.reqparse.add_argument('description',
                                   type=unicode, default="", location='json')
        self.reqparse.add_argument('link', type=unicode, location='json')
        self.reqparse.add_argument('site_link',
                                   type=unicode, default="", location='json')
        self.reqparse.add_argument('email_notification',
                                   type=bool, default=False, location='json')
        self.reqparse.add_argument('enabled',
                                   type=bool, default=True, location='json')
        super(FeedListAPI, self).__init__()

    def get(self):
        """
        Returns a list of feeds.
        """
        return {'result': [{"id": feed.id,
                            "title": feed.title,
                            "description": feed.description,
                            "link": feed.link,
                            "site_link": feed.site_link,
                            "email_notification": feed.email_notification,
                            "enabled": feed.enabled,
                            "created_date": feed.created_date,
                           } for feed in g.user.feeds]}

    def post(self):
        """
        POST method - Create a new feed.
        """
        args = self.reqparse.parse_args()
        feed_dict = {}
        for k, v in args.iteritems():
            if v != None:
                feed_dict[k] = v
            else:
                return {'message': 'missing argument: %s' % (k,)}, 400
        new_feed = Feed(title=feed_dict["title"],
                        description=feed_dict["description"],
                        link=feed_dict["link"],
                        site_link=feed_dict["site_link"],
                        email_notification=feed_dict["email_notification"],
                        enabled=feed_dict["enabled"])
        g.user.feeds.append(new_feed)
        try:
            db.session.commit()
            return {"message": "ok"}
        except:
            return {'message': 'Impossible to create the feed.'}, 500


class FeedAPI(PyAggResource):
    "Defines a RESTful API for Feed elements."
    method_decorators = [authenticate, to_response]
    db_cls = Feed

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=unicode, location='json')
        self.reqparse.add_argument('description',
                                   type=unicode, location='json')
        self.reqparse.add_argument('link', type=unicode, location='json')
        self.reqparse.add_argument('site_link', type=unicode, location='json')
        self.reqparse.add_argument('email_notification',
                                   type=bool, location='json')
        self.reqparse.add_argument('enabled', type=bool ,location='json')
        super(FeedAPI, self).__init__()

    def put(self, id):
        "Update a feed"
        args = self.reqparse.parse_args()
        feed = self.get_feed_or_raise(id)
        if 'title' in args:
            feed.title = args['title']
        if 'description' in args:
            feed.description = args['description']
        if 'link' in args:
            feed.link = args['link']
        if 'site_link' in args:
            feed.site_link = args['site_link']
        if 'email_notification' in args:
            feed.email_notification = args['email_notification']
        if 'enabled' in args:
            feed.enabled = args['enabled']
        db.session.commit()
        return {"message": "ok"}


api.add_resource(FeedListAPI, '/api/v1.0/feeds', endpoint = 'feeds.json')
api.add_resource(FeedAPI, '/api/v1.0/feeds/<int:id>', endpoint = 'feed.json')

#! /usr/bin/env python
#-*- coding: utf-8 -*-

from threading import Thread
from functools import wraps

from flask import g

from pyaggr3g470r.models import Feed

def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target = f, args = args, kwargs = kwargs)
        thr.start()
    return wrapper

def feed_access_required(func):
    """
    This decorator enables to check if a user has access to a feed.
    The administrator of the platform is able to access to the feeds of a normal user.
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        if kwargs.get('feed_id', None) != None:
            feed = Feed.query.filter(Feed.id == kwargs.get('feed_id', None)).first()
            if (feed == None or feed.subscriber.id != g.user.id) and not g.user.is_admin():
                flash("This feed do not exist.", "danger")
                return redirect(url_for('home'))
        return func(*args, **kwargs)
    return decorated

#! /usr/bin/env python
#-*- coding: utf-8 -*-

from threading import Thread
from functools import wraps

from flask import g, redirect, url_for, flash

from pyaggr3g470r.models import Feed


def async(f):
    """
    This decorator enables to launch a task (for examle sending an email or
    indexing the database) in background.
    This prevent the server to freeze.
    """
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

def feed_access_required(func):
    """
    This decorator enables to check if a user has access to a feed.
    The administrator of the platform is able to access to the feeds
    of a normal user.
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        if kwargs.get('feed_id', None) is not None:
            feed = Feed.query.filter(Feed.id == kwargs.get('feed_id', None)).first()
            if feed is not None and (feed.subscriber.id == g.user.id or g.user.is_admin()):
                return func(*args, **kwargs)
            flash("This feed do not exist.", "danger")
            return redirect(url_for('home'))
        else:
            return func(*args, **kwargs)
    return decorated

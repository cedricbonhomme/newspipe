#! /usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread
from functools import wraps

from flask_login import login_required


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


def pyagg_default_decorator(func):
    @login_required
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

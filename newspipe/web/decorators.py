#! /usr/bin/env python
from functools import wraps
from threading import Thread

from flask import current_app
from flask_login import login_required


def async_maker(f):
    """
    This decorator enables to launch a task (for example sending an email or
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


def login_required_if(config_key):
    """
    Requires an authenticated user only if the configuration flag
    `config_key` is True. The flag is read at request time.
    """

    def decorator(func):
        protected = login_required(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_app.config.get(config_key, False):
                return protected(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator

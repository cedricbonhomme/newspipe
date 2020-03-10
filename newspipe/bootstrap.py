#! /usr/bin/env python
# -*- coding: utf-8 -

# required imports and code execution for basic functionning

import os
import logging
from urllib.parse import urlsplit
from flask import request
from flask_babel import Babel, format_datetime


def set_logging(
    log_path=None,
    log_level=logging.INFO,
    modules=(),
    log_format="%(asctime)s %(levelname)s %(message)s",
):
    if not modules:
        modules = (
            "root",
            "bootstrap",
            "runserver",
            "web",
            "crawler.default_crawler",
            "manager",
            "plugins",
        )
    if log_path:
        if not os.path.exists(os.path.dirname(log_path)):
            os.makedirs(os.path.dirname(log_path))
        if not os.path.exists(log_path):
            open(log_path, "w").close()
        handler = logging.FileHandler(log_path)
    else:
        handler = logging.StreamHandler()
    formater = logging.Formatter(log_format)
    handler.setFormatter(formater)
    for logger_name in modules:
        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)
        for handler in logger.handlers:
            handler.setLevel(log_level)
        logger.setLevel(log_level)


from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create Flask application
application = Flask(__name__, instance_relative_config=True)
if os.environ.get("Newspipe_TESTING", False) == "true":
    application.debug = logging.DEBUG
    application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    application.config["TESTING"] = True
else:
    try:
        application.config.from_pyfile("development.py", silent=False)
    except Exception:
        application.config.from_pyfile("production.py", silent=False)

# scheme, domain, _, _, _ = urlsplit(conf.PLATFORM_URL)
# application.config["SERVER_NAME"] = domain
# application.config["PREFERRED_URL_SCHEME"] = scheme

set_logging(application.config["LOG_PATH"])

db = SQLAlchemy(application)


babel = Babel(application)


@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    # user = getattr(g, 'user', None)
    # if user is not None:
    #     return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(["fr", "en"])

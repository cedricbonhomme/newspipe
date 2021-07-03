#! /usr/bin/env python
# -*- coding: utf-8 -

# required imports and code execution for basic functionning

import calendar
import logging
import os

from flask import Flask, request
from flask_migrate import Migrate
from flask_talisman import Talisman
from flask_babel import Babel, format_datetime
from flask_sqlalchemy import SQLAlchemy


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
            "newspipe.crawler.default_crawler",
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


# Create Flask application
application = Flask(__name__, instance_relative_config=True)
configuration = os.environ.get("NEWSPIPE_CONFIG", False)
if configuration == "testing":
    application.debug = logging.DEBUG
    application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    application.config["TESTING"] = True
elif configuration:
    # if the configuration file is specified via an environment variable
    application.config.from_pyfile(configuration, silent=False)
else:
    try:
        application.config.from_pyfile("development.py", silent=False)
    except Exception:
        application.config.from_pyfile("sqlite.py", silent=False)

set_logging(application.config["LOG_PATH"])

db = SQLAlchemy(application)

migrate = Migrate(application, db)

talisman = Talisman(
    application, content_security_policy=application.config["CONTENT_SECURITY_POLICY"]
)

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
    return request.accept_languages.best_match(application.config["LANGUAGES"].keys())


# Jinja filters
def month_name(month_number):
    return calendar.month_name[month_number]


def datetimeformat(value, format="%Y-%m-%d %H:%M"):
    return value.strftime(format)


application.jinja_env.filters["month_name"] = month_name
application.jinja_env.filters["datetime"] = format_datetime
application.jinja_env.filters["datetimeformat"] = datetimeformat
# inject application in Jinja env
application.jinja_env.globals["application"] = application

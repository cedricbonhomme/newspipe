#! /usr/bin/env python
# -*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2015  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : https://bitbucket.org/cedricbonhomme/pyaggr3g470r/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from bootstrap import conf, application, db
from flask.ext.babel import Babel
from flask.ext.babel import format_datetime

if conf.ON_HEROKU:
    from flask_sslify import SSLify
    SSLify(application)

ALLOWED_EXTENSIONS = set(['xml', 'opml', 'json'])

def allowed_file(filename):
    """
    Check if the uploaded file is allowed.
    """
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

babel = Babel(application)

application.jinja_env.filters['datetime'] = format_datetime

# Views
from flask.ext.restful import Api
from flask import g

with application.app_context():
    g.api = Api(application, prefix='/api/v1.0')
    g.babel = babel
    g.allowed_file = allowed_file
    g.db = db
    g.app = application

    from pyaggr3g470r import views
    application.register_blueprint(views.articles_bp)
    application.register_blueprint(views.article_bp)
    application.register_blueprint(views.feeds_bp)
    application.register_blueprint(views.feed_bp)


if __name__ == '__main__':
    application.run(host=conf.WEBSERVER_HOST,
                    port=conf.WEBSERVER_PORT,
                    debug=conf.WEBSERVER_DEBUG)

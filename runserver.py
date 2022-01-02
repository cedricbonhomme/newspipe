#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Newspipe - A web news aggregator.
# Copyright (C) 2010-2022 Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information: https://sr.ht/~cedric/newspipe
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
from flask import g
from flask_restful import Api

from newspipe.bootstrap import application
from newspipe import commands


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.db_empty)
    app.cli.add_command(commands.db_create)
    app.cli.add_command(commands.fetch_asyncio)
    app.cli.add_command(commands.create_admin)


with application.app_context():
    g.api = Api(application, prefix="/api/v2.0")

    from newspipe.web import views

    application.register_blueprint(views.articles_bp)
    application.register_blueprint(views.article_bp)
    application.register_blueprint(views.feeds_bp)
    application.register_blueprint(views.feed_bp)
    application.register_blueprint(views.categories_bp)
    application.register_blueprint(views.category_bp)
    application.register_blueprint(views.icon_bp)
    application.register_blueprint(views.admin_bp)
    application.register_blueprint(views.user_bp)
    application.register_blueprint(views.bookmarks_bp)
    application.register_blueprint(views.bookmark_bp)
    application.register_blueprint(views.stats_bp)

    register_commands(application)


if __name__ == "__main__":
    application.run(
        host=application.config["HOST"],
        port=application.config["PORT"],
        debug=application.config["DEBUG"],
    )

#! /usr/bin/env python
# -*- coding: utf-8 -*-

# JARR - A Web based news aggregator.
# Copyright (C) 2010-2016  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : http://github.com/JARR/JARR
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2016/04/29 $"
__revision__ = "$Date: 2016/04/29 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

from flask_login import current_user
from web import models
from bootstrap import application, manager
from web.controllers import FeedController
from web.views.api.v3.common import AbstractProcessor
from web.views.api.v3.common import url_prefix, auth_func

class FeedProcessor(AbstractProcessor):
    """Concrete processors for the Feed Web service.
    """

    def get_single_preprocessor(self, instance_id=None, **kw):
        # Check if the user is authorized to modify the specified
        # instance of the model.
        feed = FeedController(current_user.id).get(id=instance_id)
        self.is_authorized(current_user, feed)

feed_processor = FeedProcessor()

blueprint_feed = manager.create_api_blueprint(models.Feed,
        url_prefix=url_prefix,
        methods=['GET', 'POST', 'PUT', 'DELETE'],
        preprocessors=dict(GET_SINGLE=[auth_func,
                                    feed_processor.get_single_preprocessor],
                           GET_MANY=[auth_func,
                                    feed_processor.get_many_preprocessor],
                           PUT_SINGLE=[auth_func],
                           POST=[auth_func],
                           DELETE=[auth_func]))
application.register_blueprint(blueprint_feed)

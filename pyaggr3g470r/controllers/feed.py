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

import logging
from datetime import datetime, timedelta
from werkzeug.exceptions import NotFound

import conf
from .abstract import AbstractController
from .icon import IconController
from pyaggr3g470r.models import Feed

logger = logging.getLogger(__name__)
DEFAULT_LIMIT = 5
DEFAULT_REFRESH_RATE = 60
DEFAULT_MAX_ERROR = conf.DEFAULT_MAX_ERROR


class FeedController(AbstractController):
    _db_cls = Feed

    def list_late(self, max_last, max_error=DEFAULT_MAX_ERROR,
                  limit=DEFAULT_LIMIT):
        return [feed for feed in self.read(
                            error_count__lt=max_error, enabled=True,
                            last_retrieved__lt=max_last)
                                .order_by('Feed.last_retrieved')
                                .limit(limit)]

    def list_fetchable(self, max_error=DEFAULT_MAX_ERROR, limit=DEFAULT_LIMIT,
                       refresh_rate=DEFAULT_REFRESH_RATE):
        now = datetime.now()
        max_last = now - timedelta(minutes=refresh_rate)
        feeds = self.list_late(max_last, max_error, limit)
        if feeds:
            self.update({'id__in': [feed.id for feed in feeds]},
                        {'last_retrieved': now})
        return feeds

    def _ensure_icon(self, attrs):
        if not attrs.get('icon_url'):
            return
        icon_contr = IconController()
        try:
            icon_contr.get(url=attrs['icon_url'])
        except NotFound:
            icon_contr.create(**{'url': attrs['icon_url']})

    def create(self, **attrs):
        self._ensure_icon(attrs)
        return super().create(**attrs)

    def update(self, filters, attrs):
        self._ensure_icon(attrs)
        return super().update(filters, attrs)

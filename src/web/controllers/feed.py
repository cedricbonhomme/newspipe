#! /usr/bin/env python
# -*- coding: utf-8 -*-

# jarr - A Web based news aggregator.
# Copyright (C) 2010-2016  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : https://github.com/JARR-aggregator/JARR/
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
import itertools
from datetime import datetime, timedelta

import conf
from .abstract import AbstractController
from .icon import IconController
from web.models import Feed
from web.lib.utils import clear_string

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
                                .order_by('last_retrieved')
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

    def get_duplicates(self, feed_id):
        """
        Compare a list of documents by pair.
        Pairs of duplicates are sorted by "retrieved date".
        """
        feed = self.get(id=feed_id)
        duplicates = []
        for pair in itertools.combinations(feed.articles, 2):
            date1, date2 = pair[0].date, pair[1].date
            if clear_string(pair[0].title) == clear_string(pair[1].title) \
                    and (date1 - date2) < timedelta(days=1):
                if pair[0].retrieved_date < pair[1].retrieved_date:
                    duplicates.append((pair[0], pair[1]))
                else:
                    duplicates.append((pair[1], pair[0]))
        return feed, duplicates

    def get_inactives(self, nb_days):
        today = datetime.now()
        inactives = []
        for feed in self.read():
            try:
                last_post = feed.articles[0].date
            except IndexError:
                continue
            elapsed = today - last_post
            if elapsed > timedelta(days=nb_days):
                inactives.append((feed, elapsed))
        inactives.sort(key=lambda tup: tup[1], reverse=True)
        return inactives

    def count_by_category(self, **filters):
        return self._count_by(Feed.category_id, filters)

    def _ensure_icon(self, attrs):
        if not attrs.get('icon_url'):
            return
        icon_contr = IconController()
        if not icon_contr.read(url=attrs['icon_url']).count():
            icon_contr.create(**{'url': attrs['icon_url']})

    def create(self, **attrs):
        self._ensure_icon(attrs)
        return super().create(**attrs)

    def update(self, filters, attrs):
        from .article import ArticleController
        self._ensure_icon(attrs)
        if 'category_id' in attrs:
            art_contr = ArticleController(self.user_id)
            for feed in self.read(**filters):
                art_contr.update({'feed_id': feed.id},
                                 {'category_id': attrs['category_id']})
        return super().update(filters, attrs)

import logging
import itertools
from datetime import datetime, timedelta

from bootstrap import db
from .abstract import AbstractController
from web.models.tag import BookmarkTag

logger = logging.getLogger(__name__)


class BookmarkTagController(AbstractController):
    _db_cls = BookmarkTag

    def count_by_href(self, **filters):
        return self._count_by(BookmarkTag.text, filters)

    def create(self, **attrs):
        return super().create(**attrs)

    def update(self, filters, attrs):
        return super().update(filters, attrs)

import logging
import itertools
from datetime import datetime, timedelta

from bootstrap import db
from .abstract import AbstractController
from web.models import Bookmark

logger = logging.getLogger(__name__)


class BookmarkController(AbstractController):
    _db_cls = Bookmark

    def count_by_href(self, **filters):
        return self._count_by(Bookmark.href, filters)

    def update(self, filters, attrs, *args, **kwargs):
        self.tags = attrs['tags']
        return super().update(filters, attrs, *args, **kwargs)

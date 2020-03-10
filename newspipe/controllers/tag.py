import itertools
import logging

from newspipe.bootstrap import db
from newspipe.models.tag import BookmarkTag

from .abstract import AbstractController

logger = logging.getLogger(__name__)


class BookmarkTagController(AbstractController):
    _db_cls = BookmarkTag

    def count_by_href(self, **filters):
        return self._count_by(BookmarkTag.text, filters)

    def create(self, **attrs):
        return super().create(**attrs)

    def update(self, filters, attrs):
        return super().update(filters, attrs)

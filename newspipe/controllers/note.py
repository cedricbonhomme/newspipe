import logging

from .abstract import AbstractController
from newspipe.models import ArticleNote

logger = logging.getLogger(__name__)


class ArticleNoteController(AbstractController):
    _db_cls = ArticleNote

    def read_ordered(self, **filters):
        return super().read(**filters).order_by(ArticleNote.created_date.asc())

    def read_ordered_desc(self, **filters):
        return super().read(**filters).order_by(ArticleNote.created_date.desc())

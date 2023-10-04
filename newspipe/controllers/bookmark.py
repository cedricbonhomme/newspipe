import logging

from flask_login import current_user

from newspipe.models import Bookmark

from .abstract import AbstractController
from .tag import BookmarkTagController

logger = logging.getLogger(__name__)


class BookmarkController(AbstractController):
    _db_cls = Bookmark

    def count_by_href(self, **filters):
        return self._count_by(Bookmark.href, filters)

    def read_ordered(self, **filters):
        return super().read(**filters).order_by(Bookmark.time.desc())

    def update(self, filters, attrs):
        BookmarkTagController(self.user_id).read(
            **{"bookmark_id": filters["id"]}
        ).delete()
        for tag in attrs["tags"]:
            if tag:
                BookmarkTagController(self.user_id).create(
                    **{
                        "text": tag.strip(),
                        "user_id": current_user.id,
                        "bookmark_id": filters["id"],
                    }
                )
        del attrs["tags"]
        return super().update(filters, attrs)

import logging
from datetime import datetime, timedelta

from .abstract import AbstractController
from pyaggr3g470r.models import Feed

logger = logging.getLogger(__name__)
DEFAULT_MAX_ERROR = 6
DEFAULT_LIMIT = 5


class FeedController(AbstractController):
    _db_cls = Feed

    def list_late(self, max_last, max_error=DEFAULT_MAX_ERROR,
                  limit=DEFAULT_LIMIT):
        return [feed for feed in self.read(
                            error_count__lt=max_error, enabled=True,
                            last_retrieved__lt=max_last)
                                .order_by('Feed.last_retrieved')
                                .limit(limit)]

    def list_fetchable(self, max_error=DEFAULT_MAX_ERROR, limit=DEFAULT_LIMIT):
        from pyaggr3g470r.controllers import UserController
        now = datetime.now()
        user = UserController(self.user_id).get(id=self.user_id)
        max_last = now - timedelta(minutes=user.refresh_rate or 60)
        feeds = self.list_late(max_last, max_error, limit)
        if feeds:
            self.update({'id__in': [feed.id for feed in feeds]},
                        {'last_retrieved': now})
        return feeds

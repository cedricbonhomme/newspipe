from datetime import datetime, timedelta
from .abstract import AbstractController
from pyaggr3g470r.models import Feed

DEFAULT_MAX_ERROR = 3
DEFAULT_LIMIT = 100


class FeedController(AbstractController):
    _db_cls = Feed

    def list_fetchable(self, max_error=DEFAULT_MAX_ERROR, limit=DEFAULT_LIMIT):
        from pyaggr3g470r.controllers import UserController
        now = datetime.now()
        user = UserController(self.user_id).get(id=self.user_id)
        #max_last = now - timedelta(minutes=user.refresh_rate or 60)
        feeds = [feed for feed in self.read(user_id=self.user_id,
                            error_count__lt=max_error, enabled=True).limit(limit)]
                            #last_retrieved__lt=max_last).limit(limit)]
        """if feeds:
            self.update({'id__in': [feed.id for feed in feeds]},
                        {'last_retrieved': now})"""
        return feeds

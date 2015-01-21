from datetime import datetime, timedelta
from .abstract import AbstractController
from pyaggr3g470r.models import Feed

DEFAULT_MAX_ERROR = 3
DEFAULT_LIMIT = 5


class FeedController(AbstractController):
    _db_cls = Feed

    def list_fetchable(self, max_error=DEFAULT_MAX_ERROR, limit=DEFAULT_LIMIT):
        from pyaggr3g470r.controllers import UserController
        now = datetime.now()
        user = UserController(self.user_id).get(id=self.user_id)
        max_last_refresh = now - timedelta(minutes=user.refresh_rate or 60)
        feeds = [feed for feed in self.read(user_id=self.user_id,
                          error_count__le=max_error,
                          last_modified=max_last_refresh).limit(limit)]

        self.update({'id__in': [feed.id for feed in feeds]},
                    {'last_modified': now})
        return feeds

    def list_last_articles(self, feed_id, limit=50):
        from pyaggr3g470r.controllers import ArticleController
        return ArticleController(self.user_id)._get(feed_id=feed_id)\
                .order_by(ArticleController._db_cls.retrieved_date.desc())\
                .limit(limit)

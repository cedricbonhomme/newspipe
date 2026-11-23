import itertools
import logging
from collections import defaultdict
from datetime import datetime
from datetime import timedelta

from sqlalchemy import desc
from sqlalchemy import func

from .abstract import AbstractController
from .icon import IconController
from newspipe.bootstrap import application
from newspipe.lib.utils import clear_string
from newspipe.models import Article
from newspipe.models import Feed
from newspipe.models import User

logger = logging.getLogger(__name__)
DEFAULT_LIMIT = 5
DEFAULT_MAX_ERROR = application.config["DEFAULT_MAX_ERROR"]


class FeedController(AbstractController):
    _db_cls = Feed

    def list_late(self, max_last, max_error=DEFAULT_MAX_ERROR, limit=DEFAULT_LIMIT):
        return [
            feed
            for feed in self.read(
                error_count__lt=max_error, enabled=True, last_retrieved__lt=max_last
            )
            .join(User)
            .filter(User.is_active == True)  # noqa
            .order_by("last_retrieved")
            .limit(limit)
        ]

    def list_fetchable(self, max_error=DEFAULT_MAX_ERROR, limit=DEFAULT_LIMIT):
        now = datetime.now()
        max_last = now - timedelta(minutes=60)
        feeds = self.list_late(max_last, max_error, limit)
        if feeds:
            self.update(
                {"id__in": [feed.id for feed in feeds]}, {"last_retrieved": now}
            )
        return feeds

    def get_duplicates(self, feed_id):
        """
        Find pairs of articles of a feed with the same title, published
        less than a day apart, among the 1000 most recent ones.
        Each pair is ordered by "retrieved date" (oldest first).

        Only the columns the duplicates page needs are loaded, and articles
        are grouped by cleaned title so only same-title articles are
        compared, instead of every possible pair.
        """
        from .article import ArticleController

        feed = self.get(id=feed_id)
        rows = (
            ArticleController(self.user_id)
            .read(feed_id=feed.id)
            .with_entities(
                Article.id, Article.title, Article.date, Article.retrieved_date
            )
            .order_by(desc(Article.date))
            .limit(1000)
            .all()
        )
        groups = defaultdict(list)
        for index, row in enumerate(rows):
            if row.date is not None:
                groups[clear_string(row.title or "")].append((index, row))

        found = []
        for group in groups.values():
            # Rows are sorted by date, newest first, as in the full listing.
            for (i, art1), (j, art2) in itertools.combinations(group, 2):
                if art1.date - art2.date < timedelta(days=1):
                    if art1.retrieved_date < art2.retrieved_date:
                        found.append(((i, j), (art1, art2)))
                    else:
                        found.append(((i, j), (art2, art1)))
        found.sort(key=lambda item: item[0])
        return feed, [pair for _, pair in found]

    def get_inactives(self, nb_days):
        """
        Return the feeds whose most recent article is older than nb_days,
        with the time elapsed since then, most inactive first.
        """
        from .article import ArticleController

        last_posts = dict(
            ArticleController(self.user_id)
            .read()
            .with_entities(Article.feed_id, func.max(Article.date))
            .order_by(None)
            .group_by(Article.feed_id)
            .all()
        )
        today = datetime.now()
        inactives = []
        for feed in self.read():
            last_post = last_posts.get(feed.id)
            if last_post is None:
                continue
            elapsed = today - last_post
            if elapsed > timedelta(days=nb_days):
                inactives.append((feed, elapsed))
        inactives.sort(key=lambda tup: tup[1], reverse=True)
        return inactives

    def count_by_category(self, **filters):
        return self._count_by(Feed.category_id, filters)

    def count_by_link(self, **filters):
        return self._count_by(Feed.link, filters)

    def _ensure_icon(self, attrs):
        if not attrs.get("icon_url"):
            return
        icon_contr = IconController()
        if not icon_contr.read(url=attrs["icon_url"]).count():
            icon_contr.create(**{"url": attrs["icon_url"]})

    def create(self, **attrs):
        assert "link" in attrs, "A feed must have a link."
        self._ensure_icon(attrs)
        return super().create(**attrs)

    def update(self, filters, attrs):
        from .article import ArticleController

        self._ensure_icon(attrs)
        if "category_id" in attrs:
            art_contr = ArticleController(self.user_id)
            for feed in self.read(**filters):
                art_contr.update(
                    {"feed_id": feed.id}, {"category_id": attrs["category_id"]}
                )
        return super().update(filters, attrs)

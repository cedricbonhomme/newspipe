import logging
from collections import Counter

import sqlalchemy
from sqlalchemy import func

from newspipe.bootstrap import db
from newspipe.controllers import CategoryController, FeedController
from newspipe.lib.article_utils import process_filters
from newspipe.models import Article

from .abstract import AbstractController

logger = logging.getLogger(__name__)


class ArticleController(AbstractController):
    _db_cls = Article

    def challenge(self, ids):
        """Will return each id that wasn't found in the database."""
        for id_ in ids:
            if self.read(**id_).first():
                continue
            yield id_

    def count_by_category(self, **filters):
        return self._count_by(Article.category_id, filters)

    def count_by_feed(self, **filters):
        return self._count_by(Article.feed_id, filters)

    def count_by_user_id(self, **filters):
        return dict(
            db.session.query(Article.user_id, func.count(Article.id))
            .filter(*self._to_filters(**filters))
            .group_by(Article.user_id)
            .all()
        )

    def create(self, **attrs):
        # handling special denorm for article rights
        assert "feed_id" in attrs, "must provide feed_id when creating article"
        feed = FeedController(attrs.get("user_id", self.user_id)).get(
            id=attrs["feed_id"]
        )
        if "user_id" in attrs:
            assert feed.user_id == attrs["user_id"] or self.user_id is None, (
                "no right on feed %r" % feed.id
            )
        attrs["user_id"], attrs["category_id"] = feed.user_id, feed.category_id

        skipped, read, liked = process_filters(feed.filters, attrs)
        if skipped:
            return None
        article = super().create(**attrs)
        return article

    def update(self, filters, attrs):
        user_id = attrs.get("user_id", self.user_id)
        if "feed_id" in attrs:
            feed = FeedController().get(id=attrs["feed_id"])
            assert feed.user_id == user_id, "no right on feed %r" % feed.id
            attrs["category_id"] = feed.category_id
        if attrs.get("category_id"):
            cat = CategoryController().get(id=attrs["category_id"])
            assert self.user_id is None or cat.user_id == user_id, (
                "no right on cat %r" % cat.id
            )
        return super().update(filters, attrs)

    def get_history(self, year=None, month=None):
        """
        Sort articles by year and month.
        """
        articles_counter = Counter()
        articles = self.read_light()
        if year is not None:
            articles = articles.filter(sqlalchemy.extract("year", Article.date) == year)
            if month is not None:
                articles = articles.filter(
                    sqlalchemy.extract("month", Article.date) == month
                )
        if year is not None:
            for article in articles.all():
                articles_counter[article.date.month] += 1
        else:
            for article in articles.all():
                articles_counter[article.date.year] += 1
        return articles_counter, articles

    def read_light(self, **filters):
        return (
            super()
            .read(**filters)
            .with_entities(
                Article.id,
                Article.title,
                Article.readed,
                Article.like,
                Article.feed_id,
                Article.date,
                Article.category_id,
            )
            .order_by(Article.date.desc())
        )

    def read_ordered(self, **filters):
        return super().read(**filters).order_by(Article.date.desc())

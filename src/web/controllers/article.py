import re
import logging
import sqlalchemy
from sqlalchemy import func
from collections import Counter

from bootstrap import db
from .abstract import AbstractController
from web.controllers import CategoryController, FeedController
from web.models import Article

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
        return dict(db.session.query(Article.user_id, func.count(Article.id))
                              .filter(*self._to_filters(**filters))
                              .group_by(Article.user_id).all())

    def create(self, **attrs):
        # handling special denorm for article rights
        assert 'feed_id' in attrs, "must provide feed_id when creating article"
        feed = FeedController(
                attrs.get('user_id', self.user_id)).get(id=attrs['feed_id'])
        if 'user_id' in attrs:
            assert feed.user_id == attrs['user_id'] or self.user_id is None, \
                    "no right on feed %r" % feed.id
        attrs['user_id'], attrs['category_id'] = feed.user_id, feed.category_id

        # handling feed's filters
        for filter_ in feed.filters or []:
            match = False
            if filter_.get('type') == 'regex':
                match = re.match(filter_['pattern'], attrs.get('title', ''))
            elif filter_.get('type') == 'simple match':
                match = filter_['pattern'] in attrs.get('title', '')
            take_action = match and filter_.get('action on') == 'match' \
                    or not match and filter_.get('action on') == 'no match'

            if not take_action:
                continue

            if filter_.get('action') == 'mark as read':
                attrs['readed'] = True
                logger.warn("article %s will be created as read",
                            attrs['link'])
            elif filter_.get('action') == 'mark as favorite':
                attrs['like'] = True
                logger.warn("article %s will be created as liked",
                            attrs['link'])

        return super().create(**attrs)

    def update(self, filters, attrs):
        user_id = attrs.get('user_id', self.user_id)
        if 'feed_id' in attrs:
            feed = FeedController().get(id=attrs['feed_id'])
            assert feed.user_id == user_id, "no right on feed %r" % feed.id
            attrs['category_id'] = feed.category_id
        if attrs.get('category_id'):
            cat = CategoryController().get(id=attrs['category_id'])
            assert cat.user_id == user_id, "no right on cat %r" % cat.id
        return super().update(filters, attrs)

    def get_history(self, year=None, month=None):
        """
        Sort articles by year and month.
        """
        articles_counter = Counter()
        articles = self.read()
        if year is not None:
            articles = articles.filter(
                    sqlalchemy.extract('year', Article.date) == year)
            if month is not None:
                articles = articles.filter(
                        sqlalchemy.extract('month', Article.date) == month)
        for article in articles.all():
            if year is not None:
                articles_counter[article.date.month] += 1
            else:
                articles_counter[article.date.year] += 1
        return articles_counter, articles

    def read_light(self, **filters):
        return super().read(**filters).with_entities(Article.id, Article.title,
                Article.readed, Article.like, Article.feed_id, Article.date,
                Article.category_id).order_by(Article.date.desc())

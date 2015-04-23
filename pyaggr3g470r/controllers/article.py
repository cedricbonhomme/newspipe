from sqlalchemy import func

from bootstrap import db
from .abstract import AbstractController
from pyaggr3g470r.models import Article


class ArticleController(AbstractController):
    _db_cls = Article

    def get(self, **filters):
        article = super(ArticleController, self).get(**filters)
        if not article.readed:
            self.update({'id': article.id}, {'readed': True})
        return article

    def challenge(self, ids):
        """Will return each id that wasn't found in the database."""
        for id_ in ids:
            if self.read(**id_).first():
                continue
            yield id_

    def get_unread(self):
        return dict(db.session.query(Article.feed_id, func.count(Article.id))
                       .filter(*self._to_filters(readed=False,
                                                 user_id=self.user_id))
                       .group_by(Article.feed_id).all())

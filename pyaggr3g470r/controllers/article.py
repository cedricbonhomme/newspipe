import conf
from .abstract import AbstractController
from pyaggr3g470r.models import Article


class ArticleController(AbstractController):
    _db_cls = Article

    def get(self, **filters):
        article = super(ArticleController, self).get(**filters)
        if not article.readed:
            self.update({'id': article.id}, {'readed': True})
        return article

    def delete(self, obj_id):
        obj = super(ArticleController, self).delete(obj_id)
        if not conf.ON_HEROKU:
            import pyaggr3g470r.search as fastsearch
            fastsearch.delete_article(self.user_id, obj.feed_id, obj_id)
        return obj

    def challenge(self, ids):
        """Will return each id that wasn't found in the database."""
        for id_ in ids:
            if self.read(**id_).first():
                continue
            yield id_

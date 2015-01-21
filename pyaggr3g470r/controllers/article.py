import conf
from .abstract import AbstractController
from pyaggr3g470r.models import Article


class ArticleController(AbstractController):
    _db_cls = Article

    def get(self, **filters):
        article = super(ArticleController, self).read(**filters)
        if not article.readed:
            self.update(article.id, readed=True)
        return article

    def delete(self, obj_id):
        obj = super(ArticleController, self).delete(obj_id)
        if not conf.ON_HEROKU:
            import pyaggr3g470r.search as fastsearch
            fastsearch.delete_article(self.user_id, obj.feed_id, obj_id)
        return obj

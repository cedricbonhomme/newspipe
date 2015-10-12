from .abstract import AbstractController
from web.models import Category
from .feed import FeedController


class CategoryController(AbstractController):
    _db_cls = Category

    def delete(self, obj_id):
        FeedController(self.user_id).update({'category_id': obj_id},
                                            {'category_id': None})
        return super().delete(obj_id)

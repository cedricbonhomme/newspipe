from .abstract import AbstractController
from pyaggr3g470r.models import Category


class CategoryController(AbstractController):
    _db_cls = Category

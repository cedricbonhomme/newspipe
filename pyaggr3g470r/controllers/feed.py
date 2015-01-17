from .abstract import AbstractController
from pyaggr3g470r.models import Feed


class FeedController(AbstractController):
    _db_cls = Feed

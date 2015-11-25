from .abstract import AbstractController
from web.models import User


class UserController(AbstractController):
    _db_cls = User
    _user_id_key = 'id'

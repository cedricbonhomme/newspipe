from .abstract import AbstractController
from pyaggr3g470r.models import User


class UserController(AbstractController):
    _db_cls = User
    _user_id_key = 'email'

import logging
from werkzeug import generate_password_hash, check_password_hash
from .abstract import AbstractController
from web.models import User

logger = logging.getLogger(__name__)


class UserController(AbstractController):
    _db_cls = User
    _user_id_key = 'id'

    def _handle_password(self, attrs):
        if attrs.get('password'):
            attrs['pwdhash'] = generate_password_hash(attrs.pop('password'))
        elif 'password' in attrs:
            del attrs['password']

    def check_password(self, user, password):
        return check_password_hash(user.pwdhash, password)

    def create(self, **attrs):
        self._handle_password(attrs)
        return super().create(**attrs)

    def update(self, filters, attrs):
        self._handle_password(attrs)
        return super().update(filters, attrs)

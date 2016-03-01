from bootstrap import db
from sqlalchemy import Index
from web.models.right_mixin import RightMixin


class Category(db.Model, RightMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    idx_category_uid = Index('user_id')

    # api whitelists
    @staticmethod
    def _fields_base_read():
        return {'id', 'user_id'}

    @staticmethod
    def _fields_base_write():
        return {'name'}

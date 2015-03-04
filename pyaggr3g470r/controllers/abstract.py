import logging
from bootstrap import db
from sqlalchemy import update
from werkzeug.exceptions import Forbidden, NotFound

logger = logging.getLogger(__name__)


class AbstractController(object):
    _db_cls = None  # reference to the database class
    _user_id_key = 'user_id'

    def __init__(self, user_id):
        self.user_id = user_id

    def _to_filters(self, **filters):
        if self.user_id:
            filters[self._user_id_key] = self.user_id
        db_filters = set()
        for key, value in filters.items():
            if key.endswith('__gt'):
                db_filters.add(getattr(self._db_cls, key[:-4]) > value)
            elif key.endswith('__lt'):
                db_filters.add(getattr(self._db_cls, key[:-4]) < value)
            elif key.endswith('__ge'):
                db_filters.add(getattr(self._db_cls, key[:-4]) >= value)
            elif key.endswith('__le'):
                db_filters.add(getattr(self._db_cls, key[:-4]) <= value)
            elif key.endswith('__ne'):
                db_filters.add(getattr(self._db_cls, key[:-4]) != value)
            elif key.endswith('__in'):
                db_filters.add(getattr(self._db_cls, key[:-4]).in_(value))
            else:
                db_filters.add(getattr(self._db_cls, key) == value)
        return db_filters

    def _get(self, **filters):
        return self._db_cls.query.filter(*self._to_filters(**filters))

    def get(self, **filters):
        obj = self._get(**filters).first()
        if not obj:
            raise NotFound({'message': 'No %r (%r)'
                                % (self._db_cls.__class__.__name__, filters)})
        if getattr(obj, self._user_id_key) != self.user_id:
            raise Forbidden({'message': 'No authorized to access %r (%r)'
                                % (self._db_cls.__class__.__name__, filters)})
        return obj

    def create(self, **attrs):
        attrs[self._user_id_key] = self.user_id
        obj = self._db_cls(**attrs)
        db.session.add(obj)
        db.session.commit()
        return obj

    def read(self, **filters):
        return self._get(**filters)

    def update(self, filters, attrs):
        result = self._get(**filters).update(attrs, synchronize_session=False)
        db.session.commit()
        return result

    def delete(self, obj_id):
        obj = self.get(id=obj_id)
        db.session.delete(obj)
        db.session.commit()
        return obj

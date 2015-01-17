from flask import g
from pyaggr3g470r.lib.exceptions import Forbidden, NotFound


class AbstractController(object):
    _db_cls = None

    def __init__(self, user_id):
        self.user_id = user_id

    def _get(self, **filters):
        if self.user_id:
            filters['user_id'] = self.user_id
        db_filters = [getattr(self._db_cls, key) == value
                      for key, value in filters.iteritems()]
        return self._db_cls.query.filter(*db_filters).first()

    def get(self, **filters):
        obj = self._get(**filters).first()
        if not obj:
            raise NotFound({'message': 'No %r (%r)'
                                % (self._db_cls.__class__.__name__, filters)})
        if obj.user_id != self.user_id:
            raise Forbidden({'message': 'No authorized to access %r (%r)'
                                % (self._db_cls.__class__.__name__, filters)})
        return obj

    def create(self, **attrs):
        obj = self._db_cls(**attrs)
        g.db.session.commit()
        return obj

    def read(self, **filters):
        return self._get(**filters)

    def update(self, obj_id, **attrs):
        obj = self.get(id=obj_id)
        for key, values in attrs.iteritems():
            setattr(obj, key, values)
        g.db.session.commit()
        return obj

    def delete(self, obj_id):
        obj = self.get(id=obj_id)
        g.db.session.delete(obj)
        g.db.session.commit()
        return obj

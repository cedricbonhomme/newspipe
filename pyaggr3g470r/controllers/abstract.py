import logging
from flask import g
from bootstrap import db
from sqlalchemy import or_
from werkzeug.exceptions import Forbidden, NotFound

logger = logging.getLogger(__name__)


class AbstractController(object):
    _db_cls = None  # reference to the database class
    _user_id_key = 'user_id'

    def __init__(self, user_id=None):
        """User id is a right management mechanism that should be used to
        filter objects in database on their denormalized "user_id" field
        (or "id" field for users).
        Should no user_id be provided, the Controller won't apply any filter
        allowing for a kind of "super user" mode.
        """
        self.user_id = user_id
        try:
            if self.user_id is not None \
                    and self.user_id != g.user.id and not g.user.is_admin():
                self.user_id = g.user.id
        except RuntimeError:  # passing on out of context errors
            pass

    def _to_filters(self, **filters):
        """
        Will translate filters to sqlalchemy filter.
        This method will also apply user_id restriction if available.

        each parameters of the function is treated as an equality unless the
        name of the parameter ends with either "__gt", "__lt", "__ge", "__le",
        "__ne", "__in" ir "__like".
        """
        db_filters = set()
        for key, value in filters.items():
            if key == '__or__':
                db_filters.add(or_(*self._to_filters(**value)))
            elif key.endswith('__gt'):
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
            elif key.endswith('__like'):
                db_filters.add(getattr(self._db_cls, key[:-6]).like(value))
            elif key.endswith('__ilike'):
                db_filters.add(getattr(self._db_cls, key[:-7]).ilike(value))
            else:
                db_filters.add(getattr(self._db_cls, key) == value)
        return db_filters

    def _get(self, **filters):
        """ Will add the current user id if that one is not none (in which case
        the decision has been made in the code that the query shouldn't be user
        dependant) and the user is not an admin and the filters doesn't already
        contains a filter for that user.
        """
        if self._user_id_key is not None and self.user_id \
                and filters.get(self._user_id_key) != self.user_id:
            filters[self._user_id_key] = self.user_id
        return self._db_cls.query.filter(*self._to_filters(**filters))

    def get(self, **filters):
        """Will return one single objects corresponding to filters"""
        obj = self._get(**filters).first()

        if obj and not self._has_right_on(obj):
            raise Forbidden({'message': 'No authorized to access %r (%r)'
                                % (self._db_cls.__class__.__name__, filters)})
        if not obj:
            raise NotFound({'message': 'No %r (%r)'
                                % (self._db_cls.__class__.__name__, filters)})
        return obj

    def create(self, **attrs):
        assert self._user_id_key is None or self._user_id_key in attrs \
                or self.user_id is not None, \
                "You must provide user_id one way or another"

        if self._user_id_key is not None and self._user_id_key not in attrs:
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

    def _has_right_on(self, obj):
        # user_id == None is like being admin
        if self._user_id_key is None:
            return True
        return self.user_id is None \
                or getattr(obj, self._user_id_key, None) == self.user_id

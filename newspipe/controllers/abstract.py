import logging
from collections import defaultdict
from datetime import datetime

import dateutil.parser
from sqlalchemy import func
from sqlalchemy import or_
from werkzeug.exceptions import Forbidden
from werkzeug.exceptions import NotFound

from newspipe.bootstrap import db

logger = logging.getLogger(__name__)


class AbstractController:
    _db_cls = None  # reference to the database class
    _user_id_key = "user_id"

    def __init__(self, user_id=None, ignore_context=False):
        """User id is a right management mechanism that should be used to
        filter objects in database on their denormalized "user_id" field
        (or "id" field for users).
        Should no user_id be provided, the Controller won't apply any filter
        allowing for a kind of "super user" mode.
        """
        try:
            self.user_id = int(user_id)
        except TypeError:
            self.user_id = user_id

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
            if key == "__or__":
                db_filters.add(or_(*self._to_filters(**value)))
            elif key.endswith("__gt"):
                db_filters.add(getattr(self._db_cls, key[:-4]) > value)
            elif key.endswith("__lt"):
                db_filters.add(getattr(self._db_cls, key[:-4]) < value)
            elif key.endswith("__ge"):
                db_filters.add(getattr(self._db_cls, key[:-4]) >= value)
            elif key.endswith("__le"):
                db_filters.add(getattr(self._db_cls, key[:-4]) <= value)
            elif key.endswith("__ne"):
                db_filters.add(getattr(self._db_cls, key[:-4]) != value)
            elif key.endswith("__in"):
                db_filters.add(getattr(self._db_cls, key[:-4]).in_(value))
            elif key.endswith("__contains"):
                db_filters.add(getattr(self._db_cls, key[:-10]).contains(value))
            elif key.endswith("__like"):
                db_filters.add(getattr(self._db_cls, key[:-6]).like(value))
            elif key.endswith("__ilike"):
                db_filters.add(getattr(self._db_cls, key[:-7]).ilike(value))
            else:
                db_filters.add(getattr(self._db_cls, key) == value)
        return db_filters

    def _get(self, **filters):
        """Will add the current user id if that one is not none (in which case
        the decision has been made in the code that the query shouldn't be user
        dependent) and the user is not an admin and the filters doesn't already
        contains a filter for that user.
        """
        if (
            self._user_id_key is not None
            and self.user_id
            and filters.get(self._user_id_key) != self.user_id
        ):
            filters[self._user_id_key] = self.user_id
        return self._db_cls.query.filter(*self._to_filters(**filters))

    def get(self, **filters):
        """Will return one single objects corresponding to filters"""
        obj = self._get(**filters).first()

        if obj and not self._has_right_on(obj):
            raise Forbidden(
                {
                    "message": "No authorized to access %r (%r)"
                    % (self._db_cls.__class__.__name__, filters)
                }
            )
        if not obj:
            raise NotFound(
                {"message": f"No {self._db_cls.__class__.__name__!r} ({filters!r})"}
            )
        return obj

    def create(self, commit=True, validate=True, **attrs):
        """
        Create a new ORM object.

        :param commit: whether to flush and commit after adding the object
        :param validate: whether to rely on SQLAlchemy validators (@validates)
        :param attrs: attributes to initialize the object with
        """
        assert attrs, "attributes to create must not be empty"

        # Inject user_id if controller is scoped to a user
        if self._user_id_key is not None and self._user_id_key not in attrs:
            attrs[self._user_id_key] = self.user_id

        assert (
            self._user_id_key is None
            or self._user_id_key in attrs
            or self.user_id is None
        ), "You must provide user_id one way or another"

        # Instantiate ORM object (this triggers validators on init)
        obj = self._db_cls(**attrs)

        # If validators are disabled, manually insert without object construction
        if not validate:
            # Use the table directly for a fast insert (no ORM events)
            db.session.execute(db.insert(self._db_cls.__table__).values(**attrs))
            if commit:
                db.session.flush()
                db.session.commit()
            # Refetch ORM instance if needed
            return (
                db.session.query(self._db_cls).order_by(self._db_cls.id.desc()).first()
            )

        # Normal ORM path (validates, sanitizes, etc.)
        db.session.add(obj)
        if commit:
            db.session.flush()
            db.session.commit()

        return obj

    def read(self, **filters):
        return self._get(**filters)

    def update(self, filters, attrs, return_objs=False, commit=True, validate=True):
        """
        Update one or more ORM objects.

        :param filters: dict of filters to locate objects
        :param attrs: dict of attributes to update
        :param return_objs: whether to return ORM objects instead of count
        :param commit: whether to flush and commit at the end
        :param validate: if True, trigger SQLAlchemy validators (@validates)
        """
        assert attrs, "attributes to update must not be empty"

        query = self._get(**filters)

        # Detect if filters uniquely identify a single record
        # e.g., {"id": 123}, {"uuid": "..."} — you can extend the list if needed
        single_object = "id" in filters or "uuid" in filters

        if validate:
            # Fetch only one object when possible
            objs = [query.first()] if single_object else query.all()
            objs = [obj for obj in objs if obj is not None]
            if not objs:
                return [] if return_objs else 0

            for obj in objs:
                for key, value in attrs.items():
                    # Avoid triggering validators unnecessarily
                    if getattr(obj, key) != value:
                        setattr(obj, key, value)

            result = objs
        else:
            # Fast path — bypass ORM (no validators)
            updated = query.update(attrs, synchronize_session=False)
            result = self._get(**filters).all() if return_objs else updated

        if commit:
            db.session.flush()
            db.session.commit()

        return result if return_objs else len(result)

    def delete(self, obj_id):
        obj = self.get(id=obj_id)
        db.session.delete(obj)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
        return obj

    def _has_right_on(self, obj):
        # user_id == None is like being admin
        if self._user_id_key is None:
            return True
        return (
            self.user_id is None
            or getattr(obj, self._user_id_key, None) == self.user_id
        )

    def _count_by(self, elem_to_group_by, filters):
        if self.user_id:
            filters["user_id"] = self.user_id
        return dict(
            db.session.query(elem_to_group_by, func.count("id"))
            .filter(*self._to_filters(**filters))
            .group_by(elem_to_group_by)
            .all()
        )

    @classmethod
    def _get_attrs_desc(cls, role, right=None):
        result = defaultdict(dict)
        if role == "admin":
            columns = cls._db_cls.__table__.columns.keys()
        else:
            assert role in {"base", "api"}, "unknown role %r" % role
            assert right in {"read", "write"}, (
                "right must be 'read' or 'write' with role %r" % role
            )
            columns = getattr(cls._db_cls, f"fields_{role}_{right}")()
        for column in columns:
            result[column] = {}
            db_col = getattr(cls._db_cls, column).property.columns[0]
            try:
                result[column]["type"] = db_col.type.python_type
            except NotImplementedError:
                if db_col.default:
                    result[column]["type"] = db_col.default.arg.__class__
            if column not in result:
                continue
            if issubclass(result[column]["type"], datetime):
                result[column]["default"] = datetime.utcnow()
                result[column]["type"] = lambda x: dateutil.parser.parse(x)
            elif db_col.default:
                result[column]["default"] = db_col.default.arg
        return result

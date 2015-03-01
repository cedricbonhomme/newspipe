import json
import logging
import dateutil.parser
from copy import deepcopy
from functools import wraps
from werkzeug.exceptions import Unauthorized
from flask import request, g, session, Response
from flask.ext.restful import Resource, reqparse

from pyaggr3g470r.lib.utils import default_handler
from pyaggr3g470r.models import User

logger = logging.getLogger(__name__)


def authenticate(func):
    """
    Decorator for the authentication to the web services.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logged_in = False
        if not getattr(func, 'authenticated', True):
            logged_in = True
        # authentication based on the session (already logged on the site)
        elif 'email' in session or g.user.is_authenticated():
            logged_in = True
        else:
            # authentication via HTTP only
            auth = request.authorization
            user = User.query.filter(User.nickname == auth.username).first()
            if user and user.check_password(auth.password) \
                    and user.activation_key == "":
                g.user = user
                logged_in = True

        if logged_in:
            return func(*args, **kwargs)
        raise Unauthorized({'WWWAuthenticate': 'Basic realm="Login Required"'})
    return wrapper


def to_response(func):
    def wrapper(*args, **kwargs):
        status_code = 200
        result = func(*args, **kwargs)
        if isinstance(result, Response):
            return result
        elif isinstance(result, tuple):
            result, status_code = result
        return Response(json.dumps(result, default=default_handler),
                        status=status_code)
    return wrapper


class PyAggAbstractResource(Resource):
    method_decorators = [authenticate, to_response]
    attrs = {}
    to_date = []

    def __init__(self, *args, **kwargs):
        super(PyAggAbstractResource, self).__init__(*args, **kwargs)

    @property
    def controller(self):
        return self.controller_cls(getattr(g.user, 'id', None))

    def reqparse_args(self, req=None, strict=False, default=True, args=None):
        """
        strict: bool
            if True will throw 400 error if args are defined and not in request
        default: bool
            if True, won't return defaults
        """
        parser = reqparse.RequestParser()
        for attr_name, attrs in (args or self.attrs).items():
            if attrs.pop('force_default', False):
                parser.add_argument(attr_name, location='json', **attrs)
            elif not default and (not request.json
                    or request.json and attr_name not in request.json):
                continue
            else:
                parser.add_argument(attr_name, location='json', **attrs)
        parsed = parser.parse_args(strict=strict) if req is None \
                else parser.parse_args(req, strict=strict)
        for field in self.to_date:
            if parsed.get(field):
                try:
                    parsed[field] = dateutil.parser.parse(parsed[field])
                except Exception:
                    logger.exception('failed to parse %r', parsed[field])
        return parsed


class PyAggResourceNew(PyAggAbstractResource):

    def post(self):
        return self.controller.create(**self.reqparse_args()), 201


class PyAggResourceExisting(PyAggAbstractResource):

    def get(self, obj_id=None):
        return self.controller.get(id=obj_id)

    def put(self, obj_id=None):
        args = self.reqparse_args(default=False)
        new_values = {key: args[key] for key in
                      set(args).intersection(self.attrs)}
        self.controller.update({'id': obj_id}, new_values)

    def delete(self, obj_id=None):
        self.controller.delete(obj_id)
        return None, 204


class PyAggResourceMulti(PyAggAbstractResource):

    def get(self):
        args = deepcopy(self.attrs)
        args['limit'] = {'type': int, 'default': 10, 'force_default': True}
        filters = self.reqparse_args(default=False, strict=False, args=args)
        limit = filters.pop('limit', None)
        if not limit:
            return [res for res in self.controller.read(**filters).all()]
        return [res for res in self.controller.read(**filters).limit(limit)]

    def post(self):
        status = 201
        results = []
        args = []  # FIXME
        for arg in args:
            try:
                results.append(self.controller.create(**arg).id)
            except Exception as error:
                status = 206
                results.append(error)
        return results, status

    def put(self):
        status = 200
        results = []
        args = {}  # FIXME
        for obj_id, attrs in args.items():
            try:
                new_values = {key: args[key] for key in
                              set(attrs).intersection(self.editable_attrs)}
                self.controller.update({'id': obj_id}, new_values)
                results.append('ok')
            except Exception as error:
                status = 206
                results.append(error)
        return results, status

    def delete(self):
        status = 204
        results = []
        obj_ids = []  # FIXME extract some real ids
        for obj_id in obj_ids:
            try:
                self.controller.delete(obj_id)
                results.append('ok')
            except Exception as error:
                status = 206
                results.append(error)
        return results, status

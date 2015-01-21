import json
import types
from functools import wraps
from flask import request, g, session, Response
from flask.ext.restful import Resource, reqparse

from pyaggr3g470r.models import User
from pyaggr3g470r.lib.exceptions import PyAggError


def authenticate(func):
    """
    Decorator for the authentication to the web services.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not getattr(func, 'authenticated', True):
            return func(*args, **kwargs)

        # authentication based on the session (already logged on the site)
        if 'email' in session or g.user.is_authenticated():
            return func(*args, **kwargs)

        # authentication via HTTP only
        auth = request.authorization
        try:
            email = auth.username
            user = User.query.filter(User.email == email).first()
            if user and user.check_password(auth.password) and user.activation_key == "":
                g.user = user
                return func(*args, **kwargs)
        except AttributeError:
            pass

        return Response('<Authentication required>', 401,
                        {'WWWAuthenticate':'Basic realm="Login Required"'})
    return wrapper


def default_handler(obj):
    """JSON handler for default query formatting"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    if hasattr(obj, 'dump'):
        return obj.dump()
    if isinstance(obj, (set, frozenset, types.GeneratorType)):
        return list(obj)
    raise TypeError("Object of type %s with value of %r "
                    "is not JSON serializable" % (type(obj), obj))


def to_response(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except PyAggError as error:
            response = Response(json.dumps(result[0], default=default_handler))
            response.status_code = error.status_code
            return response
        status_code = 200
        if isinstance(result, tuple):
            result, status_code = result
        response = Response(json.dumps(result, default=default_handler),
                            status=status_code)
        return response
    return wrapper


class PyAggAbstractResource(Resource):
    method_decorators = [authenticate, to_response]

    def __init__(self, *args, **kwargs):
        self.controller = self.controller_cls(g.user.id)
        super(PyAggAbstractResource, self).__init__(*args, **kwargs)

    def reqparse_args(self, strict=False, default=True):
        """
        strict: bool
            if True will throw 400 error if args are defined and not in request
        default: bool
            if True, won't return defaults

        """
        parser = reqparse.RequestParser()
        for attr_name, attrs in self.attrs.items():
            if not default and attr_name not in request.args:
                continue
            parser.add_argument(attr_name, location='json', **attrs)
        return parser.parse_args(strict=strict)


class PyAggResourceNew(PyAggAbstractResource):

    def post(self):
        return self.controller.create(**self.reqparse_args()), 201


class PyAggResourceExisting(PyAggAbstractResource):

    def get(self, obj_id=None):
        return self.controller.get(id=obj_id).dump()

    def put(self, obj_id=None):
        args = self.reqparse_args()
        new_values = {key: args[key] for key in
                      set(args).intersection(self.attrs)}
        self.controller.update(obj_id, **new_values)

    def delete(self, obj_id=None):
        self.controller.delete(obj_id)
        return None, 204


class PyAggResourceMulti(PyAggAbstractResource):

    def get(self):
        filters = self.reqparse_args(default=False)
        return [res.dump() for res in self.controller.read(**filters).all()]

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
                self.controller.update(obj_id, **new_values)
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

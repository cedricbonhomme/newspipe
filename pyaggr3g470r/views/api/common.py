from functools import wraps
from flask import request, g, session, Response, jsonify
from flask.ext.restful import Resource

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


def to_response(func):
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
        except PyAggError, error:
            response = jsonify(**error.message)
            response.status_code = error.status_code
            return response
        if isinstance(res, tuple):
            response = jsonify(**res[0])
            if len(res) > 1:
                response.status_code = res[1]
            return response
        return res
    return wrapper


class PyAggResource(Resource):
    method_decorators = [authenticate, to_response]
    controller_cls = None
    editable_attrs = []

    def __init__(self, *args, **kwargs):
        self.controller = self.controller_cls(g.user.id)
        super(PyAggResource, self).__init__(*args, **kwargs)

    def get(self, obj_id=None):
        return {'result': [self.controller.read(id=obj_id).dump()]}

    def put(self, obj_id=None):
        args = self.reqparse.parse_args()
        new_values = {key: args[key] for key in
                      set(args).intersection(self.editable_attrs)}
        self.controller.update(obj_id, **new_values)
        return {"message": "ok"}

    def delete(self, obj_id=None):
        self.controller.delete(obj_id)
        return {"message": "ok"}, 204

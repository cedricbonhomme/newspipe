from functools import wraps
from flask import request, g, session, Response, jsonify
from flask.ext.restful import Resource

from pyaggr3g470r import db
from pyaggr3g470r.models import User


class HttpError(Exception):
    pass


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
        except HttpError, error:
            return Response(*error.args)
        if isinstance(res, tuple):
            response = jsonify(**res[0])
            if len(res) > 1:
                response.status_code = res[1]
            return response
        return res
    return wrapper


class PyAggResource(Resource):
    db_cls = None

    def _get_or_raise(self, obj_id=None):
        if obj_id is None:
            raise HttpError({'message': 'No id given'}, 400)
        obj = self.db_cls.query.filter(self.db_cls.id == obj_id).first()
        if obj is None:
            raise HttpError({'message': 'Article not found'}, 404)
        if obj.user_id != g.user.id:
            raise HttpError({'message': "Unauthorized for %s."
                                    % self.db_cls.__class__.__name__}, 403)
        return obj

    def get(self, id=None):
        return {'result': [self._get_or_raise(id).dump()]}

    def delete(self, id):
        """Delete a feed."""
        feed = self._get_or_raise(id)
        db.session.delete(feed)
        db.session.commit()
        return {"message": "ok"}, 204

#! /usr/bin/env python
# -*- coding: utf-8 -

"""For a given resources, classes in the module intend to create the following
routes :
    GET resource/<id>
        -> to retrieve one
    POST resource
        -> to create one
    PUT resource/<id>
        -> to update one
    DELETE resource/<id>
        -> to delete one

    GET resources
        -> to retrieve several
    POST resources
        -> to create several
    PUT resources
        -> to update several
    DELETE resources
        -> to delete several
"""
import json
import logging
import dateutil.parser
from functools import wraps
from werkzeug.exceptions import Unauthorized, BadRequest
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
        elif 'email' in session or g.user.is_authenticated:
            logged_in = True
        else:
            # authentication via HTTP only
            auth = request.authorization
            if auth is not None:
                user = User.query.filter(
                        User.nickname == auth.username).first()
                if user and user.check_password(auth.password) \
                        and user.activation_key == "":
                    g.user = user
                    logged_in = True
        if logged_in:
            return func(*args, **kwargs)
        raise Unauthorized({'WWWAuthenticate': 'Basic realm="Login Required"'})
    return wrapper


def to_response(func):
    """Will cast results of func as a result, and try to extract
    a status_code for the Response object"""
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
    to_date = []  # list of fields to cast to datetime

    def __init__(self, *args, **kwargs):
        super(PyAggAbstractResource, self).__init__(*args, **kwargs)

    @property
    def controller(self):
        return self.controller_cls(getattr(g.user, 'id', None))

    @property
    def wider_controller(self):
        if g.user.is_admin():
            return self.controller_cls()
        return self.controller_cls(getattr(g.user, 'id', None))

    def reqparse_args(self, req=None, strict=False, default=True, args=None):
        """
        strict: bool
            if True will throw 400 error if args are defined and not in request
        default: bool
            if True, won't return defaults
        args: dict
            the args to parse, if None, self.attrs will be used
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
        """Create a single new object"""
        return self.controller.create(**self.reqparse_args()), 201


class PyAggResourceExisting(PyAggAbstractResource):

    def get(self, obj_id=None):
        """Retreive a single object"""
        return self.controller.get(id=obj_id)

    def put(self, obj_id=None):
        """update an object, new attrs should be passed in the payload"""
        args = self.reqparse_args(default=False)
        new_values = {key: args[key] for key in
                      set(args).intersection(self.attrs)}
        if 'user_id' in new_values and g.user.is_admin():
            controller = self.wider_controller
        else:
            controller = self.controller
        return controller.update({'id': obj_id}, new_values), 200

    def delete(self, obj_id=None):
        """delete a object"""
        self.controller.delete(obj_id)
        return None, 204


class PyAggResourceMulti(PyAggAbstractResource):

    def get(self):
        """retrieve several objects. filters can be set in the payload on the
        different fields of the object, and a limit can be set in there as well
        """
        try:
            limit = request.json.pop('limit', 10)
            order_by = request.json.pop('order_by', None)
            query = self.controller.read(**request.json)
        except:
            limit, order_by, query = 10, None, self.controller.read()
        if order_by:
            query = query.order_by(order_by)
        if limit:
            query = query.limit(limit)
        return [res for res in query]

    def post(self):
        """creating several objects. payload should be a list of dict.
        """
        if 'application/json' not in request.headers.get('Content-Type'):
            raise BadRequest("Content-Type must be application/json")
        status = 201
        results = []
        for attrs in request.json:
            try:
                results.append(self.controller.create(**attrs).id)
            except Exception as error:
                status = 206
                results.append(str(error))
        # if no operation succeded, it's not partial anymore, returning err 500
        if status == 206 and results.count('ok') == 0:
            status = 500
        return results, status

    def put(self):
        """creating several objects. payload should be:
        >>> payload
        [[obj_id1, {attr1: val1, attr2: val2}]
         [obj_id2, {attr1: val1, attr2: val2}]]
        """
        if 'application/json' not in request.headers.get('Content-Type'):
            raise BadRequest("Content-Type must be application/json")
        status = 200
        results = []
        for obj_id, attrs in request.json:
            try:
                new_values = {key: attrs[key] for key in
                              set(attrs).intersection(self.attrs)}
                self.controller.update({'id': obj_id}, new_values)
                results.append('ok')
            except Exception as error:
                status = 206
                results.append(str(error))
        # if no operation succeded, it's not partial anymore, returning err 500
        if status == 206 and results.count('ok') == 0:
            status = 500
        return results, status

    def delete(self):
        """will delete several objects,
        a list of their ids should be in the payload"""
        if 'application/json' not in request.headers.get('Content-Type'):
            raise BadRequest("Content-Type must be application/json")
        status = 204
        results = []
        for obj_id in request.json:
            try:
                self.controller.delete(obj_id)
                results.append('ok')
            except Exception as error:
                status = 206
                results.append(error)
        # if no operation succeded, it's not partial anymore, returning err 500
        if status == 206 and results.count('ok') == 0:
            status = 500
        return results, status

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
import ast
import logging
from functools import wraps
from werkzeug.exceptions import Unauthorized, BadRequest, Forbidden, NotFound
from flask import request
from flask_restful import Resource, reqparse
from flask_login import current_user

from web.views.common import admin_permission, api_permission, \
                             login_user_bundle, jsonify
from web.controllers import UserController

logger = logging.getLogger(__name__)


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.authorization:
            ucontr = UserController()
            try:
                user = ucontr.get(nickname=request.authorization.username)
            except NotFound:
                raise Forbidden("Couldn't authenticate your user")
            if not ucontr.check_password(user, request.authorization.password):
                raise Forbidden("Couldn't authenticate your user")
            if not user.is_active:
                raise Forbidden("User is deactivated")
            login_user_bundle(user)
        if current_user.is_authenticated:
            return func(*args, **kwargs)
        raise Unauthorized()
    return wrapper


class PyAggAbstractResource(Resource):
    method_decorators = [authenticate, jsonify]
    controller_cls = None
    attrs = None

    @property
    def controller(self):
        if admin_permission.can():
            return self.controller_cls()
        return self.controller_cls(current_user.id)

    def reqparse_args(self, right, req=None, strict=False, default=True,
                      allow_empty=False):
        """
        strict: bool
            if True will throw 400 error if args are defined and not in request
        default: bool
            if True, won't return defaults
        args: dict
            the args to parse, if None, self.attrs will be used
        """
        try:
            if req:
                in_values = req.json
            else:
                in_values = request.args or request.json or {}
            if not in_values and allow_empty:
                return {}
        except BadRequest:
            if allow_empty:
                return {}
            raise
        parser = reqparse.RequestParser()
        if self.attrs is not None:
            attrs = self.attrs
        elif admin_permission.can():
            attrs = self.controller_cls._get_attrs_desc('admin')
        elif api_permission.can():
            attrs = self.controller_cls._get_attrs_desc('api', right)
        else:
            attrs = self.controller_cls._get_attrs_desc('base', right)
        assert attrs, "No defined attrs for %s" % self.__class__.__name__

        for attr_name, attr in attrs.items():
            if not default and attr_name not in in_values:
                continue
            else:
                parser.add_argument(attr_name, location='json',
                                        default=in_values[attr_name])
        return parser.parse_args(req=request.args, strict=strict)


class PyAggResourceNew(PyAggAbstractResource):

    @api_permission.require(http_exception=403)
    def post(self):
        """Create a single new object"""
        return self.controller.create(**self.reqparse_args(right='write')), 201


class PyAggResourceExisting(PyAggAbstractResource):

    def get(self, obj_id=None):
        """Retrieve a single object"""
        return self.controller.get(id=obj_id)

    def put(self, obj_id=None):
        """update an object, new attrs should be passed in the payload"""
        args = self.reqparse_args(right='write', default=False)
        if not args:
            raise BadRequest()
        return self.controller.update({'id': obj_id}, args), 200

    def delete(self, obj_id=None):
        """delete a object"""
        self.controller.delete(obj_id)
        return None, 204


class PyAggResourceMulti(PyAggAbstractResource):

    def get(self):
        """retrieve several objects. filters can be set in the payload on the
        different fields of the object, and a limit can be set in there as well
        """
        args = {}
        try:
            limit = request.json.pop('limit', 10)
            order_by = request.json.pop('order_by', None)
        except Exception:
            args = self.reqparse_args(right='read', default=False)
            limit = request.args.get('limit', 10)
            order_by = request.args.get('order_by', None)
        query = self.controller.read(**args)
        if order_by:
            query = query.order_by(order_by)
        if limit:
            query = query.limit(limit)
        return [res for res in query]

    @api_permission.require(http_exception=403)
    def post(self):
        """creating several objects. payload should be:
        >>> payload
        [{attr1: val1, attr2: val2}, {attr1: val1, attr2: val2}]
        """
        status, fail_count, results = 200, 0, []

        class Proxy:
            pass
        for attrs in request.json:
            try:
                Proxy.json = attrs
                args = self.reqparse_args('write', req=Proxy, default=False)
                obj = self.controller.create(**args)
                results.append(obj)
            except Exception as error:
                fail_count += 1
                results.append(str(error))
        if fail_count == len(results):  # all failed => 500
            status = 500
        elif fail_count:  # some failed => 206
            status = 206
        return results, status

    def put(self):
        """updating several objects. payload should be:
        >>> payload
        [[obj_id1, {attr1: val1, attr2: val2}]
         [obj_id2, {attr1: val1, attr2: val2}]]
        """
        status, results = 200, []

        class Proxy:
            pass
        for obj_id, attrs in request.json:
            try:
                Proxy.json = attrs
                args = self.reqparse_args('write', req=Proxy, default=False)
                result = self.controller.update({'id': obj_id}, args)
                if result:
                    results.append('ok')
                else:
                    results.append('nok')
            except Exception as error:
                results.append(str(error))
        if results.count('ok') == 0:  # all failed => 500
            status = 500
        elif results.count('ok') != len(results):  # some failed => 206
            status = 206
        return results, status

    def delete(self):
        """will delete several objects,
        a list of their ids should be in the payload"""
        status, results = 204, []
        for obj_id in request.json:
            try:
                self.controller.delete(obj_id)
                results.append('ok')
            except Exception as error:
                status = 206
                results.append(error)
        # if no operation succeeded, it's not partial anymore, returning err 500
        if status == 206 and results.count('ok') == 0:
            status = 500
        return results, status

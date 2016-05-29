import json
from functools import wraps
from datetime import datetime
from flask import current_app, Response
from flask_login import login_user
from flask_principal import (Identity, Permission, RoleNeed,
                                 session_identity_loader, identity_changed)
from web.controllers import UserController
from web.lib.utils import default_handler

admin_role = RoleNeed('admin')
api_role = RoleNeed('api')

admin_permission = Permission(admin_role)
api_permission = Permission(api_role)


def scoped_default_handler():
    if admin_permission.can():
        role = 'admin'
    elif api_permission.can():
        role = 'api'
    else:
        role = 'user'

    @wraps(default_handler)
    def wrapper(obj):
        return default_handler(obj, role=role)
    return wrapper


def jsonify(func):
    """Will cast results of func as a result, and try to extract
    a status_code for the Response object"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        status_code = 200
        result = func(*args, **kwargs)
        if isinstance(result, Response):
            return result
        elif isinstance(result, tuple):
            result, status_code = result
        return Response(json.dumps(result, default=scoped_default_handler()),
                        mimetype='application/json', status=status_code)
    return wrapper


def login_user_bundle(user):
    login_user(user)
    identity_changed.send(current_app, identity=Identity(user.id))
    session_identity_loader()
    UserController(user.id).update(
                {'id': user.id}, {'last_seen': datetime.utcnow()})

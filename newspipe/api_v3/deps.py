"""FastAPI dependencies of the modernized API.

The HTTP Basic authentication of the legacy v2 API (the ``authenticate``
decorator of ``web/views/api/v2/common.py``) becomes a single declarative
dependency reused by every migrated endpoint.

Controller and model calls need a Flask application context because the
legacy data layer is built on Flask-SQLAlchemy. Each dependency/endpoint
opens its own context explicitly: FastAPI may run dependencies and endpoint
bodies on different threads, and Flask contexts are thread-local.
"""
from dataclasses import dataclass

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials
from werkzeug.exceptions import NotFound

from newspipe.bootstrap import application
from newspipe.controllers import UserController

security = HTTPBasic()


@dataclass
class AuthUser:
    """Authenticated user detached from the SQLAlchemy session."""

    id: int
    nickname: str
    is_admin: bool
    is_api: bool


def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
) -> AuthUser:
    """Authenticate the request with HTTP Basic against the users table.

    Mirrors the legacy semantics: unknown user, wrong password or inactive
    user answer 403, missing credentials answer 401 (handled by HTTPBasic).
    """
    with application.app_context():
        ucontr = UserController()
        try:
            user = ucontr.get(nickname=credentials.username)
        except NotFound:
            raise HTTPException(403, "Couldn't authenticate your user")
        if not ucontr.check_password(user, credentials.password):
            raise HTTPException(403, "Couldn't authenticate your user")
        if not user.is_active:
            raise HTTPException(403, "User is deactivated")
        return AuthUser(
            id=user.id,
            nickname=user.nickname,
            is_admin=user.is_admin,
            is_api=user.is_api,
        )


def require_api_right(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """Equivalent of the legacy ``api_permission.require(403)`` decorator."""
    if not (user.is_api or user.is_admin):
        raise HTTPException(403, "API right required")
    return user

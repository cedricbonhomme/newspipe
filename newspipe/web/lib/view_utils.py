from functools import wraps

from flask import make_response
from flask import request
from flask import Response

from newspipe.lib.utils import to_hash


def etag_match(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if isinstance(response, Response):
            etag = to_hash(response.data)
            headers = response.headers
        elif type(response) is str:
            etag = to_hash(response)
            headers = {}
        else:
            return response
        if request.headers.get("if-none-match") == etag:
            response = Response(status=304)
            response.headers["Cache-Control"] = headers.get(
                "Cache-Control", "pragma: no-cache"
            )
        elif not isinstance(response, Response):
            response = make_response(response)
        response.headers["etag"] = etag
        return response

    return wrapper

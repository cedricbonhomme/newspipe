from functools import wraps
from flask import request, Response, make_response
from pyaggr3g470r.lib.utils import to_hash


def etag_match(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if not type(response) is str:
            return response
        etag = to_hash(response)
        if request.headers.get('if-none-match') == etag:
            response = Response(status=304, headers={'etag': etag,
                                'Cache-Control': 'pragma: no-cache'})
        else:
            response = make_response(response)
            response.headers['etag'] = etag
        return response
    return wrapper

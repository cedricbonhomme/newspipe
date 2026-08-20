from functools import wraps

from flask import make_response
from flask import request
from flask import Response
from flask_paginate import get_page_args

from newspipe.lib.utils import to_hash

# Upper bound on the number of records a single paginated page may render.
MAX_PER_PAGE = 200


def paginate_args(max_per_page=MAX_PER_PAGE, **kwargs):
    """Return the (page, per_page, offset) triple for the current request.

    Both values come straight from the query string, so both are clamped:
    an unbounded per_page lets a caller ask for the whole table in one page,
    which defeats the point of paginating, and a page below 1 builds a
    negative OFFSET, which SQLite quietly ignores but PostgreSQL rejects.

    Any other keyword argument is passed through to
    :func:`flask_paginate.get_page_args`, so each view keeps its own default
    page size.
    """
    page, per_page, _ = get_page_args(**kwargs)
    per_page = min(max(per_page, 1), max_per_page)
    page = max(page, 1)
    return page, per_page, (page - 1) * per_page


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

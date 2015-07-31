import types
import urllib
import base64
import logging
import requests
from hashlib import md5

logger = logging.getLogger(__name__)


def default_handler(obj):
    """JSON handler for default query formatting"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    if hasattr(obj, 'dump'):
        return obj.dump()
    if isinstance(obj, (set, frozenset, types.GeneratorType)):
        return list(obj)
    if isinstance(obj, BaseException):
        return str(obj)
    raise TypeError("Object of type %s with value of %r "
                    "is not JSON serializable" % (type(obj), obj))


def try_keys(dico, *keys):
    for key in keys:
        if key in dico:
            return dico[key]
    return


def rebuild_url(url, base_split):
    split = urllib.parse.urlsplit(url)
    if split.scheme and split.netloc:
        return url  # url is fine
    new_split = urllib.parse.SplitResult(
            scheme=split.scheme or base_split.scheme,
            netloc=split.netloc or base_split.netloc,
            path=split.path, query='', fragment='')
    return urllib.parse.urlunsplit(new_split)


def try_get_b64icon(url, *splits):
    for split in splits:
        if split is None:
            continue
        rb_url = rebuild_url(url, split)
        response = requests.get(rb_url, verify=False, timeout=10)
        # if html in content-type, we assume it's a fancy 404 page
        content_type = response.headers.get('content-type', '')
        if response.ok and 'html' not in content_type and response.content:
            return content_type + (
                    '\n%s' % base64.b64encode(response.content).decode('utf8'))
    return None


def to_hash(text):
    return md5(text.encode('utf8')).hexdigest()

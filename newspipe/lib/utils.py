import logging
import re
import types
from hashlib import md5
from urllib.parse import parse_qs
from urllib.parse import SplitResult
from urllib.parse import urlencode
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlsplit
from urllib.parse import urlunparse
from urllib.parse import urlunsplit

import requests  # type: ignore[import-untyped]
import urllib3
from flask import request
from flask import url_for
from pyvulnerabilitylookup import PyVulnerabilityLookup

from newspipe.bootstrap import application
from newspipe.lib.url_validation import resolve_validated_ip

logger = logging.getLogger(__name__)


def default_handler(obj, role="admin"):
    """JSON handler for default query formatting"""
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    if hasattr(obj, "dump"):
        return obj.dump(role=role)
    if isinstance(obj, (set, frozenset, types.GeneratorType)):
        return list(obj)
    if isinstance(obj, BaseException):
        return str(obj)
    raise TypeError(
        "Object of type %s with value of %r "
        "is not JSON serializable" % (type(obj), obj)
    )


def try_keys(dico, *keys):
    for key in keys:
        if key in dico:
            return dico[key]
    return


def rebuild_url(url, base_split):
    split = urlsplit(url)
    if split.scheme and split.netloc:
        return url  # URL is already complete

    new_split = SplitResult(
        scheme=split.scheme or base_split.scheme,
        netloc=split.netloc or base_split.netloc,
        path=split.path,
        query="",
        fragment="",
    )
    return urlunsplit(new_split)


def try_get_icon_url(url, *splits):
    for split in splits:
        if split is None:
            continue
        rb_url = rebuild_url(url, split)
        response = None
        # if html in content-type, we assume it's a fancy 404 page
        try:
            response = newspipe_get(rb_url)
            content_type = response.headers.get("content-type", "")
        except Exception:
            pass
        else:
            if (
                response is not None
                and response.ok
                and "html" not in content_type
                and response.content
            ):
                return response.url
    return None


def to_hash(text):
    return md5(text.encode("utf8") if hasattr(text, "encode") else text).hexdigest()


def clear_string(data):
    """
    Clear a string by removing HTML tags, HTML special characters
    and consecutive white spaces (more that one).
    """
    p = re.compile("<[^>]+>")  # HTML tags
    q = re.compile(r"\s")  # consecutive white spaces
    return p.sub("", q.sub(" ", data))


def _is_internal_url(candidate):
    """Return the absolute form of ``candidate`` if it points back at this
    application, otherwise None.

    A candidate is accepted when it resolves, relative to the current request,
    to an http(s) URL on the very same host. That rejects absolute off-site
    URLs, protocol-relative ones (``//evil.example``) and non-http schemes
    such as ``javascript:``.
    """
    try:
        resolved = urlparse(urljoin(request.host_url, candidate))
    except ValueError:
        return None
    if resolved.scheme not in ("http", "https"):
        return None
    if resolved.netloc != urlparse(request.host_url).netloc:
        return None
    # Hand back the absolute URL rather than the raw candidate: a path such as
    # "/\\evil.example" is same-host here but would be read as a
    # protocol-relative URL by the browser if echoed verbatim in Location.
    return resolved.geturl()


def safe_redirect_url(default="home"):
    """Return a URL that is safe to redirect the user to.

    Honours the ``next`` parameter, then the referrer, but only while they
    stay on this host; anything else falls back to ``default``.
    """
    for candidate in (request.args.get("next"), request.referrer):
        if not candidate:
            continue
        internal_url = _is_internal_url(candidate)
        if internal_url:
            return internal_url
    return url_for(default)


def remove_utm_parameters(url: str) -> str:
    # Parse the URL
    parsed_url = urlparse(url)

    # Parse query parameters
    query_params = parse_qs(parsed_url.query)

    # Remove all UTM parameters
    utm_keys = [key for key in query_params if key.startswith("utm_")]
    for key in utm_keys:
        del query_params[key]

    # Rebuild the query string without UTM parameters
    new_query = urlencode(query_params, doseq=True)

    # Rebuild and return the URL without UTM parameters
    new_url = urlunparse(parsed_url._replace(query=new_query))
    return new_url


_MAX_REDIRECTS = 10


class _PinnedIPHTTPConnection(urllib3.connection.HTTPConnection):
    """Connect to a pre-validated IP instead of resolving the hostname again.

    ``_dns_host`` is what urllib3 hands to ``create_connection``; ``host`` --
    used afterwards for the Host header, the SNI name and certificate
    validation -- is only read back once ``_new_conn`` has returned. Swapping
    the value for the duration of the lookup therefore redirects the
    connection without altering anything the peer gets to see.
    """

    def __init__(self, *args, pinned_ip=None, **kwargs):
        self.pinned_ip = pinned_ip
        super().__init__(*args, **kwargs)

    def _new_conn(self):
        if not self.pinned_ip:
            return super()._new_conn()
        hostname = self._dns_host
        self._dns_host = self.pinned_ip
        try:
            return super()._new_conn()
        finally:
            self._dns_host = hostname


class _PinnedIPHTTPSConnection(
    _PinnedIPHTTPConnection, urllib3.connection.HTTPSConnection
):
    pass


class _PinnedIPHTTPConnectionPool(urllib3.HTTPConnectionPool):
    ConnectionCls = _PinnedIPHTTPConnection


class _PinnedIPHTTPSConnectionPool(urllib3.HTTPSConnectionPool):
    ConnectionCls = _PinnedIPHTTPSConnection


_PINNED_IP_POOL_CLASSES = {
    "http": _PinnedIPHTTPConnectionPool,
    "https": _PinnedIPHTTPSConnectionPool,
}


class _PinnedIPPoolManager(urllib3.PoolManager):
    """PoolManager handing out pools that connect to ``pinned_ip``.

    The address is injected into each pool's ``conn_kw`` after the fact rather
    than through ``connection_pool_kw``: pools are keyed by a fixed-field
    namedtuple, so an unknown keyword there is rejected outright.
    """

    def __init__(self, pinned_ip, *args, **kwargs):
        self.pinned_ip = pinned_ip
        super().__init__(*args, **kwargs)
        self.pool_classes_by_scheme = _PINNED_IP_POOL_CLASSES

    def _new_pool(self, scheme, host, port, request_context=None):
        pool = super()._new_pool(scheme, host, port, request_context)
        pool.conn_kw["pinned_ip"] = self.pinned_ip
        return pool


class _PinnedIPAdapter(requests.adapters.HTTPAdapter):
    """Transport adapter whose connections all target ``pinned_ip``."""

    def __init__(self, pinned_ip, **kwargs):
        self._pinned_ip = pinned_ip
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        self._pool_connections = connections
        self._pool_maxsize = maxsize
        self._pool_block = block
        self.poolmanager = _PinnedIPPoolManager(
            self._pinned_ip,
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            **pool_kwargs,
        )


def _get_pinned(url, ip, **request_kwargs):
    """GET ``url``, connecting only to ``ip``."""
    with requests.Session() as session:
        # Environment proxies would route the request through a resolver we do
        # not control, silently defeating the pin. Newspipe never crawls
        # through a proxy, so opt out of them entirely.
        session.trust_env = False
        session.mount("http://", _PinnedIPAdapter(ip))
        session.mount("https://", _PinnedIPAdapter(ip))
        return session.get(url, **request_kwargs)


def newspipe_get(url, **kwargs):
    ip = resolve_validated_ip(url)
    request_kwargs = {
        "verify": False,
        "timeout": application.config["CRAWLER_TIMEOUT"],
        "headers": {"User-Agent": application.config["CRAWLER_USER_AGENT"]},
    }
    request_kwargs.update(kwargs)
    request_kwargs["allow_redirects"] = False

    response = _get_pinned(url, ip, **request_kwargs)
    for _ in range(_MAX_REDIRECTS):
        if not (response.is_redirect or response.is_permanent_redirect):
            break
        location = response.headers.get("Location")
        if not location:
            break
        url = urljoin(response.url, location)
        ip = resolve_validated_ip(url)
        response = _get_pinned(url, ip, **request_kwargs)
    return response


def remove_case_insensitive_duplicates(input_list):
    """Remove duplicates in a list, ignoring case.
    This approach preserves the last occurrence of each unique item based on
    lowercase equivalence. The dictionary keys are all lowercase to ensure
    case-insensitive comparison, while the original case is preserved in the output.
    """
    return list({item.lower(): item for item in input_list}.values())


def push_sighting_to_vulnerability_lookup(article, vulnerability_ids, sighting_type):
    """Create a sighting from an incoming article and push it to the Vulnerability Lookup instance."""
    print("Pushing sighting to Vulnerability Lookup...")
    vuln_lookup = PyVulnerabilityLookup(
        application.config["VULNERABILITY_LOOKUP_BASE_URL"],
        token=application.config["VULNERABILITY_AUTH_TOKEN"],
    )

    for vuln in vulnerability_ids:
        # Create the sighting
        sighting = {
            "type": sighting_type,
            "source": remove_utm_parameters(article.link),
            "content": article.content,
            "vulnerability": vuln,
            "creation_timestamp": article.date,
        }

        # Post the JSON to Vulnerability Lookup
        try:
            r = vuln_lookup.create_sighting(sighting=sighting)
            if "message" in r:
                print(r["message"])
        except Exception as e:
            print(
                f"Error when sending POST request to the Vulnerability Lookup server:\n{e}"
            )

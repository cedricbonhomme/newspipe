# Every redirect hop must be re-validated before it is followed.
#
# Validating only the URL the user supplied is not enough: an attacker-controlled
# host that passes validation can answer with a 302 pointing at an internal
# address. ``newspipe_get`` follows redirects itself so each hop goes through
# ``validate_url``; these tests pin that behaviour down.
import threading
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

import pytest
import requests

from newspipe.lib import feed_utils
from newspipe.lib import utils
from newspipe.lib.url_validation import SSRFError
from newspipe.lib.url_validation import validate_url as real_validate_url
from newspipe.lib.utils import newspipe_get

INTERNAL_BODY = b"internal-service-response"


class _Internal(BaseHTTPRequestHandler):
    """Stands in for an internal service (metadata endpoint, intranet, ...)."""

    def do_GET(self):
        self.server.hits += 1
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(INTERNAL_BODY)

    def log_message(self, *args):
        pass


class _Redirector(BaseHTTPRequestHandler):
    """Stands in for the attacker-controlled host the user added as a feed."""

    def do_GET(self):
        self.send_response(302)
        self.send_header("Location", self.server.target)
        self.end_headers()

    def log_message(self, *args):
        pass


def _serve(handler):
    server = HTTPServer(("127.0.0.1", 0), handler)
    server.hits = 0
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


@pytest.fixture
def redirect_chain():
    """A public-looking URL that redirects to a blocked one."""
    internal = _serve(_Internal)
    redirector = _serve(_Redirector)
    redirector.target = f"http://127.0.0.1:{internal.server_port}/latest/meta-data/"
    entry = f"http://127.0.0.1:{redirector.server_port}/feed.xml"
    try:
        yield entry, redirector.target, internal
    finally:
        internal.shutdown()
        redirector.shutdown()


@pytest.fixture
def entry_url_allowed(monkeypatch):
    """Let the entry URL through so the loopback stand-ins model a public host.

    Only the first hop is exempted; every later hop hits the real guard, which
    is what these tests are about.
    """

    def _allow(entry):
        def fake_validate_url(url):
            return url if url == entry else real_validate_url(url)

        monkeypatch.setattr(utils, "validate_url", fake_validate_url)

    return _allow


def test_redirect_to_internal_address_is_blocked(redirect_chain, entry_url_allowed):
    entry, _target, internal = redirect_chain
    entry_url_allowed(entry)

    with pytest.raises(SSRFError):
        newspipe_get(entry, timeout=5)

    assert internal.hits == 0, "the guarded fetch reached the internal service"


def test_unguarded_requests_would_follow_the_redirect(redirect_chain):
    """Control: proves the fixture really does model a reachable internal host.

    This is the behaviour ``construct_feed_from`` had before it was routed
    through ``newspipe_get``; if this test ever stops passing the others prove
    nothing.
    """
    entry, target, internal = redirect_chain

    response = requests.get(entry, timeout=5)

    assert response.url == target
    assert response.content == INTERNAL_BODY
    assert internal.hits == 1


def test_guarded_fetch_still_returns_allowed_responses(
    redirect_chain, entry_url_allowed
):
    """The guard must not break ordinary, non-redirecting fetches."""
    _entry, target, internal = redirect_chain
    entry_url_allowed(target)

    response = newspipe_get(target, timeout=5)

    assert response.content == INTERNAL_BODY
    assert internal.hits == 1


def test_construct_feed_from_uses_the_guarded_helper(monkeypatch):
    """``construct_feed_from`` must not call ``requests.get`` directly."""
    calls = []

    def spy(url, **kwargs):
        calls.append(url)
        raise SSRFError("blocked")

    monkeypatch.setattr(feed_utils, "newspipe_get", spy)

    url = "http://example.invalid/feed.xml"
    feed = feed_utils.construct_feed_from(url)

    # Both fetches it performs -- the feed itself and the site link derived from
    # it -- must go through the guarded helper rather than ``requests.get``.
    assert calls == [url, url]
    # A blocked URL yields an unusable feed rather than raising.
    assert feed["site_link"] == url


def test_construct_feed_from_does_not_follow_redirects_inward(
    redirect_chain, entry_url_allowed
):
    """End-to-end: adding a feed that redirects inward must not reach the target.

    This is the regression that mattered -- ``construct_feed_from`` used to call
    ``requests.get``, which follows redirects on its own, so only the URL the
    user typed was ever validated.
    """
    entry, _target, internal = redirect_chain
    entry_url_allowed(entry)

    feed_utils.construct_feed_from(entry)

    assert internal.hits == 0, "construct_feed_from reached the internal service"

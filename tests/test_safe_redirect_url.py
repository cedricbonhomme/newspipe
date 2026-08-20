# ``safe_redirect_url`` decides where the user lands after an action, from the
# ``next`` parameter or the referrer. Both are attacker-influenceable, so it
# must only ever hand back a URL on this host -- otherwise a link such as
# /admin/fetch?next=https://evil.example turns the app into an open redirect.
import pytest

from newspipe.bootstrap import application
from newspipe.lib.utils import safe_redirect_url

HOST = "newspipe.test"
BASE = f"http://{HOST}"

# The views are only wired up by app.py, which needs a database; the fallback
# endpoint is all these tests need, so stand it in on the bare app.
if "home" not in application.view_functions:
    application.add_url_rule("/", "home", lambda: "")


@pytest.fixture
def ctx():
    """Build a request context on HOST with the given query string/referrer."""

    def _ctx(path="/action", **kwargs):
        return application.test_request_context(path, base_url=BASE, **kwargs)

    return _ctx


@pytest.mark.parametrize(
    "candidate",
    [
        "https://evil.example/phish",
        "http://evil.example",
        "//evil.example/phish",
        r"https:/\evil.example",
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        f"http://{HOST}.evil.example/phish",
        f"http://evil.example/?x=http://{HOST}/",
    ],
)
def test_offsite_next_is_refused(ctx, candidate):
    with ctx(query_string={"next": candidate}):
        assert safe_redirect_url() == "/"


def test_offsite_referrer_is_refused(ctx):
    with ctx(headers={"Referer": "https://evil.example/phish"}):
        assert safe_redirect_url() == "/"


@pytest.mark.parametrize(
    "candidate",
    ["/home", "/category/3", f"{BASE}/bookmarks", "/home?page=2#top"],
)
def test_same_host_next_is_honoured(ctx, candidate):
    with ctx(query_string={"next": candidate}):
        assert safe_redirect_url().startswith(BASE)


def test_same_host_referrer_is_honoured(ctx):
    with ctx(headers={"Referer": f"{BASE}/bookmarks"}):
        assert safe_redirect_url() == f"{BASE}/bookmarks"


def test_next_wins_over_referrer(ctx):
    with ctx(
        query_string={"next": "/category/3"},
        headers={"Referer": f"{BASE}/bookmarks"},
    ):
        assert safe_redirect_url() == f"{BASE}/category/3"


def test_offsite_next_falls_through_to_the_referrer(ctx):
    """A rejected ``next`` is skipped, not fatal: the referrer still applies."""
    with ctx(
        query_string={"next": "https://evil.example"},
        headers={"Referer": f"{BASE}/bookmarks"},
    ):
        assert safe_redirect_url() == f"{BASE}/bookmarks"


def test_backslash_path_is_returned_absolute(ctx):
    r"""``/\evil.example`` is same-host to urlparse but scheme-relative to a
    browser, so it must never be echoed verbatim into Location."""
    with ctx(query_string={"next": r"/\evil.example"}):
        assert safe_redirect_url().startswith(f"{BASE}/")


def test_falls_back_to_the_default_endpoint(ctx):
    """The fallback has to actually work: no ``next``, no referrer, no error."""
    with ctx():
        assert safe_redirect_url() == "/"

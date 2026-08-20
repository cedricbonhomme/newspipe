# Imported OPML is user-supplied XML. ``opml.from_string`` parses it with
# lxml's default parser, whose entity handling depends on the libxml2 build we
# happen to link against; ``import_opml`` uses an explicitly hardened parser so
# an upload can never read local files or exhaust memory.
import io

import lxml.etree
import pytest

from newspipe.bootstrap import application
from newspipe.lib.data import _OPML_PARSER
from newspipe.lib.data import OPMLTooLargeError
from newspipe.lib.data import read_opml_upload

GOOD = b"""<?xml version="1.0"?>
<opml version="1.0"><head><title>My feeds</title></head>
<body>
  <outline text="News">
    <outline text="Blog &amp; more" description="d" xmlUrl="https://ex.com/f.xml"/>
  </outline>
</body></opml>"""

XXE = b"""<?xml version="1.0"?>
<!DOCTYPE opml [ <!ENTITY xxe SYSTEM "file:///etc/hostname"> ]>
<opml version="1.0"><body>
  <outline text="&xxe;" xmlUrl="http://ex.com/f.xml"/>
</body></opml>"""

EXTERNAL_DTD = (
    b'<?xml version="1.0"?>'
    b'<!DOCTYPE opml SYSTEM "http://attacker.example/x.dtd">'
    b"<opml><body/></opml>"
)

BILLION_LAUGHS = (
    b'<?xml version="1.0"?><!DOCTYPE opml ['
    + b"".join(
        b'<!ENTITY l%d "%s">' % (i, (b"&l%d;" % (i - 1)) * 10 if i else b"a" * 100)
        for i in range(9)
    )
    + b"]><opml><body>&l8;</body></opml>"
)


def parse(payload):
    return lxml.etree.fromstring(payload, _OPML_PARSER)


def test_ordinary_opml_still_parses():
    """The hardening must not cost us predefined entities or nesting."""
    import opml

    subscriptions = opml.Opml(parse(GOOD))
    assert subscriptions.title == "My feeds"
    assert subscriptions[0][0].text == "Blog & more"
    assert subscriptions[0][0].xmlUrl == "https://ex.com/f.xml"


@pytest.mark.parametrize("payload", [XXE, BILLION_LAUGHS])
def test_entity_attacks_are_refused(payload):
    with pytest.raises(lxml.etree.XMLSyntaxError):
        parse(payload)


def test_external_dtd_is_not_fetched():
    """No network call, and no exception either -- the DTD is simply ignored."""
    assert parse(EXTERNAL_DTD).tag == "opml"


# The upload is read straight into memory and lxml then builds a tree on top
# of it, so an unbounded .opml is a cheap way for a logged-in user to exhaust
# the worker. read_opml_upload() bounds what we are willing to buffer.


class _CountingStream(io.BytesIO):
    """Records how much of the stream was actually consumed."""

    def __init__(self, payload):
        super().__init__(payload)
        self.bytes_read = 0

    def read(self, size=-1):
        chunk = super().read(size)
        self.bytes_read += len(chunk)
        return chunk


@pytest.fixture
def small_limit(monkeypatch):
    monkeypatch.setitem(application.config, "OPML_MAX_SIZE", 1024)
    return 1024


def test_upload_within_the_limit_is_returned(small_limit):
    payload = b"x" * small_limit
    assert read_opml_upload(io.BytesIO(payload)) == payload


def test_oversized_upload_is_refused(small_limit):
    with pytest.raises(OPMLTooLargeError):
        read_opml_upload(io.BytesIO(b"x" * (small_limit + 1)))


def test_oversized_upload_is_not_buffered(small_limit):
    """The point of the cap: refuse without pulling the whole thing in."""
    stream = _CountingStream(b"x" * (small_limit * 100))
    with pytest.raises(OPMLTooLargeError):
        read_opml_upload(stream)
    assert stream.bytes_read == small_limit + 1


def test_import_opml_rejects_oversized_content_too(small_limit):
    """Backstop for callers that did not come through read_opml_upload()."""
    from newspipe.lib.data import import_opml

    with pytest.raises(OPMLTooLargeError):
        import_opml("nobody", b"x" * (small_limit + 1))


def test_the_shipped_default_accommodates_a_real_subscription_list():
    outline = b'<outline text="Feed" xmlUrl="https://ex.com/f.xml"/>'
    ten_thousand_feeds = b"<opml><body>" + outline * 10000 + b"</body></opml>"
    assert len(ten_thousand_feeds) < application.config["OPML_MAX_SIZE"]

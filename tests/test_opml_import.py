# Imported OPML is user-supplied XML. ``opml.from_string`` parses it with
# lxml's default parser, whose entity handling depends on the libxml2 build we
# happen to link against; ``import_opml`` uses an explicitly hardened parser so
# an upload can never read local files or exhaust memory.
import lxml.etree
import pytest

from newspipe.lib.data import _OPML_PARSER

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

# Regression tests for the SSRF guard.
#
# These lock in the behaviour the guard depends on. Most of the classification
# work is done by the stdlib ``ipaddress`` module, whose handling of IPv6
# transition encodings was corrected in CPython gh-113171 (3.10.15). Newspipe
# requires Python >= 3.13, so those fixes are always present -- these tests make
# that dependency explicit rather than implicit, so a refactor of
# ``_is_blocked_ip`` cannot silently drop a range.
import ipaddress

import pytest

from newspipe.lib.url_validation import _is_blocked_ip
from newspipe.lib.url_validation import SSRFError
from newspipe.lib.url_validation import validate_url

BLOCKED_IPS = [
    # IPv6 transition encodings wrapping an internal IPv4 address.
    ("2002:c0a8:0001::", "6to4 wrapping 192.168.0.1"),
    ("2002:a9fe:a9fe::", "6to4 wrapping 169.254.169.254"),
    ("64:ff9b::a9fe:a9fe", "NAT64 well-known prefix"),
    ("64:ff9b:1::a9fe:a9fe", "NAT64 local-use prefix"),
    ("2001:0:4136:e378:8000:63bf:3fff:fdd2", "Teredo"),
    ("::ffff:169.254.169.254", "IPv4-mapped link-local"),
    ("::ffff:127.0.0.1", "IPv4-mapped loopback"),
    ("::127.0.0.1", "IPv4-compatible loopback"),
    # Plain internal addresses.
    ("127.0.0.1", "loopback"),
    ("169.254.169.254", "cloud metadata endpoint"),
    ("10.0.0.1", "RFC1918"),
    ("192.168.0.1", "RFC1918"),
    ("172.16.0.1", "RFC1918"),
    ("0.0.0.0", "unspecified"),
    ("::1", "IPv6 loopback"),
    ("fe80::1", "IPv6 link-local"),
    ("fc00::1", "IPv6 unique-local"),
    ("ff02::1", "IPv6 multicast"),
]

ALLOWED_IPS = [
    "93.184.216.34",
    "1.1.1.1",
    "2606:4700:4700::1111",
]


@pytest.mark.parametrize("address,reason", BLOCKED_IPS, ids=[i[1] for i in BLOCKED_IPS])
def test_internal_addresses_are_blocked(address, reason):
    assert _is_blocked_ip(ipaddress.ip_address(address)) is True


@pytest.mark.parametrize("address", ALLOWED_IPS)
def test_public_addresses_are_allowed(address):
    assert _is_blocked_ip(ipaddress.ip_address(address)) is False


@pytest.mark.parametrize(
    "url",
    [
        "http://2130706433/",  # 127.0.0.1 in decimal
        "http://0177.0.0.1/",  # octal
        "http://0x7f.0x0.0x0.0x1/",  # hexadecimal
        "http://127.1/",  # short form
        "http://127.0.0.1:8080/",
        "http://user:pass@127.0.0.1/",  # host hidden behind userinfo
        "http://[::ffff:127.0.0.1]/",
        "http://[64:ff9b::a9fe:a9fe]/",
        "http://[2002:a9fe:a9fe::]/",
        "http://localhost/",
    ],
)
def test_alternate_encodings_of_internal_hosts_are_blocked(url):
    with pytest.raises(SSRFError):
        validate_url(url)


@pytest.mark.parametrize(
    "url", ["file:///etc/passwd", "gopher://example.com/", "ftp://example.com/"]
)
def test_non_http_schemes_are_rejected(url):
    with pytest.raises(SSRFError):
        validate_url(url)


def test_url_without_hostname_is_rejected():
    with pytest.raises(SSRFError):
        validate_url("http:///path")

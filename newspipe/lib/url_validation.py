import ipaddress
import logging
import socket
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)


class SSRFError(ValueError):
    """Raised when a URL fails SSRF validation."""

    pass


def validate_url(url):
    """Validate a URL to prevent Server-Side Request Forgery (SSRF).

    Ensures:
    - Only http and https schemes are allowed.
    - Hostname does not resolve to private, loopback, link-local,
      multicast, or reserved IP addresses.

    Raises SSRFError if validation fails.
    Returns the URL unchanged if valid.
    """
    resolve_validated_ip(url)
    return url


def resolve_validated_ip(url):
    """Validate ``url`` as :func:`validate_url` does and return the IP address
    its hostname resolved to.

    Callers that go on to make the request should connect to this exact
    address. Letting the HTTP client resolve the hostname a second time
    reopens a DNS-rebinding window: an attacker-controlled record can answer
    the validation lookup with a public address and the connection lookup with
    an internal one, so the address that is checked is never the address that
    is used.
    """
    parsed = urlsplit(url)

    if parsed.scheme not in ("http", "https"):
        raise SSRFError(
            f"URL scheme '{parsed.scheme}' is not allowed. "
            "Only http and https are permitted."
        )

    hostname = parsed.hostname
    if not hostname:
        raise SSRFError("URL has no hostname.")

    return _check_hostname(hostname)


def _check_hostname(hostname):
    """Resolve a hostname, verify none of its addresses are internal and
    return the first one."""
    try:
        addrinfos = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise SSRFError(f"Could not resolve hostname: {hostname}") from exc

    if not addrinfos:
        raise SSRFError(f"Could not resolve hostname: {hostname}")

    for _family, _type, _proto, _canonname, sockaddr in addrinfos:
        ip = ipaddress.ip_address(sockaddr[0])
        if _is_blocked_ip(ip):
            raise SSRFError(f"URL resolves to a blocked IP address ({ip}).")

    return addrinfos[0][4][0]


def _is_blocked_ip(ip):
    """Return True if the IP falls in a blocked range."""
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )

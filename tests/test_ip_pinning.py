# ``resolve_validated_ip`` checks the address a hostname resolves to, but the
# check is worthless if the HTTP client then resolves the hostname a second
# time: an attacker-controlled DNS record can answer the first lookup with a
# public address and the second with 127.0.0.1. ``newspipe_get`` therefore
# connects to the address that was validated, and these tests pin that down.
import socket
import threading
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

import pytest
import requests

from newspipe.lib import utils
from newspipe.lib.utils import newspipe_get

# .invalid is reserved by RFC 2606 and never resolves, so reaching the server
# through this name can only mean DNS was bypassed.
UNRESOLVABLE_HOST = "newspipe-pinning-test.invalid"


class _Echo(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.host_headers.append(self.headers.get("Host"))
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"served")

    def log_message(self, *args):
        pass


@pytest.fixture
def echo_server():
    server = HTTPServer(("127.0.0.1", 0), _Echo)
    server.host_headers = []
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield server
    finally:
        server.shutdown()


@pytest.fixture
def pinned_to_loopback(monkeypatch):
    """Pretend the unresolvable hostname validated to 127.0.0.1.

    That is exactly the split a rebinding attack creates: a name whose
    validated address and whose live DNS answer disagree.
    """
    monkeypatch.setattr(utils, "resolve_validated_ip", lambda url: "127.0.0.1")


def test_hostname_is_genuinely_unresolvable():
    """Control: without the pin there is no way to reach the server."""
    with pytest.raises(socket.gaierror):
        socket.getaddrinfo(UNRESOLVABLE_HOST, None)


def test_request_goes_to_the_validated_address(echo_server, pinned_to_loopback):
    url = f"http://{UNRESOLVABLE_HOST}:{echo_server.server_port}/feed.xml"
    response = newspipe_get(url, timeout=5)
    assert response.status_code == 200
    assert response.content == b"served"


def test_pinning_keeps_the_real_hostname_on_the_wire(echo_server, pinned_to_loopback):
    """Only the DNS lookup is redirected: the Host header (and, over TLS, the
    SNI name and certificate check) must still use the hostname."""
    port = echo_server.server_port
    newspipe_get(f"http://{UNRESOLVABLE_HOST}:{port}/feed.xml", timeout=5)
    assert echo_server.host_headers == [f"{UNRESOLVABLE_HOST}:{port}"]


def test_unpinned_client_cannot_reach_it(echo_server):
    """Control: plain requests fails, so the pin is what made it work."""
    url = f"http://{UNRESOLVABLE_HOST}:{echo_server.server_port}/feed.xml"
    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get(url, timeout=5)

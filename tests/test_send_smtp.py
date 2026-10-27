# ``send_smtp`` picks the SMTP connection from the MAIL_* settings: plain on
# MAIL_PORT, upgraded with STARTTLS (MAIL_USE_TLS) or wrapped in TLS from the
# start (MAIL_USE_SSL). The encrypted modes must verify the server certificate.
import ssl

import pytest

from newspipe.bootstrap import application
from newspipe.notifications import emails


class FakeSMTP:
    instances: list["FakeSMTP"] = []

    def __init__(self, host, port, context=None):
        self.host, self.port, self.context = host, port, context
        self.starttls_context = None
        self.logged_in = None
        self.sent = False
        FakeSMTP.instances.append(self)

    def starttls(self, context=None):
        self.starttls_context = context

    def login(self, user, password):
        self.logged_in = (user, password)

    def sendmail(self, *args):
        self.sent = True

    def quit(self):
        pass


class FakeSMTPSSL(FakeSMTP):
    pass


@pytest.fixture
def smtp(monkeypatch):
    FakeSMTP.instances = []
    monkeypatch.setattr(emails.smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(emails.smtplib, "SMTP_SSL", FakeSMTPSSL)
    for key, value in {
        "MAIL_SERVER": "smtp.example.org",
        "MAIL_USERNAME": None,
        "MAIL_PASSWORD": None,
        "MAIL_DEFAULT_SENDER": "newspipe@example.org",
    }.items():
        monkeypatch.setitem(application.config, key, value)
    for key in ("MAIL_PORT", "MAIL_USE_TLS", "MAIL_USE_SSL"):
        monkeypatch.delitem(application.config, key, raising=False)

    def _send(**config):
        for key, value in config.items():
            monkeypatch.setitem(application.config, key, value)
        emails.send_smtp(to="user@example.org", subject="Hello", plaintext="Hi")
        (conn,) = FakeSMTP.instances
        assert conn.sent
        return conn

    return _send


def _verifies_certificates(context):
    return (
        isinstance(context, ssl.SSLContext)
        and context.verify_mode == ssl.CERT_REQUIRED
        and context.check_hostname
    )


def test_defaults_to_plain_smtp_on_port_25(smtp):
    conn = smtp()
    assert type(conn) is FakeSMTP
    assert (conn.host, conn.port) == ("smtp.example.org", 25)
    assert conn.starttls_context is None


def test_custom_port(smtp):
    conn = smtp(MAIL_PORT=2525)
    assert conn.port == 2525


def test_starttls(smtp):
    conn = smtp(MAIL_PORT=587, MAIL_USE_TLS=True)
    assert type(conn) is FakeSMTP
    assert conn.port == 587
    assert _verifies_certificates(conn.starttls_context)


def test_implicit_tls(smtp):
    conn = smtp(MAIL_USE_SSL=True)
    assert type(conn) is FakeSMTPSSL
    assert conn.port == 465
    assert _verifies_certificates(conn.context)
    assert conn.starttls_context is None


def test_login_with_starttls(smtp):
    conn = smtp(MAIL_USE_TLS=True, MAIL_USERNAME="bot", MAIL_PASSWORD="secret")
    assert conn.starttls_context is not None
    assert conn.logged_in == ("bot", "secret")

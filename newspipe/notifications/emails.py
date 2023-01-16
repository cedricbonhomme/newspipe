#! /usr/bin/env python
# Newspipe - A web news aggregator.
# Copyright (C) 2010-2023 Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information: https://sr.ht/~cedric/newspipe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import logging
import smtplib
from email import charset
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from newspipe.bootstrap import application
from newspipe.web.decorators import async_maker

logger = logging.getLogger(__name__)


@async_maker
def send_async_email(mfrom, mto, msg):
    try:
        s = smtplib.SMTP(application.config["NOTIFICATION_HOST"])
        s.login(
            application.config["NOTIFICATION_USERNAME"],
            application.config["NOTIFICATION_PASSWORD"],
        )
    except Exception:
        logger.exception("send_async_email raised:")
    else:
        s.sendmail(mfrom, mto, msg.as_bytes().decode(encoding="UTF-8"))
        s.quit()


def send(*args, **kwargs):
    """
    This functions enables to send email via different method.
    """
    send_smtp(**kwargs)


def send_smtp(to="", subject="", plaintext="", html=""):
    """
    Send an email.
    """
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart("alternative")
    ch = charset.add_charset("utf-8", charset.QP)
    msg.set_charset(ch)
    msg["Subject"] = subject
    msg["From"] = application.config["MAIL_DEFAULT_SENDER"]
    msg["To"] = to

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(plaintext, "plain", "utf-8")
    # part2 = MIMEText(html, "html", "utf-8")

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    # msg.attach(part2)

    try:
        s = smtplib.SMTP(application.config["MAIL_SERVER"])
        if application.config["MAIL_USERNAME"] is not None:
            s.login(
                application.config["MAIL_USERNAME"],
                application.config["MAIL_PASSWORD"],
            )
    except Exception:
        logger.exception("send_smtp raised:")
    else:
        s.sendmail(
            application.config["MAIL_DEFAULT_SENDER"],
            msg["To"],
            msg.as_bytes().decode(encoding="UTF-8"),
        )
        s.quit()

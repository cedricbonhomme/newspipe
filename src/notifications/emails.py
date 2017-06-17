#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Newspipe - A Web based news aggregator.
# Copyright (C) 2010-2016  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : https://github.com/Newspipe/Newspipe
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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import sendgrid
from sendgrid.helpers.mail import *

import conf
from web.decorators import async

logger = logging.getLogger(__name__)


@async
def send_async_email(mfrom, mto, msg):
    try:
        s = smtplib.SMTP(conf.NOTIFICATION_HOST)
        s.login(conf.NOTIFICATION_USERNAME, conf.NOTIFICATION_PASSWORD)
    except Exception:
        logger.exception('send_async_email raised:')
    else:
        s.sendmail(mfrom, mto, msg.as_string())
        s.quit()

def send(*args, **kwargs):
    """
    This functions enables to send email through SendGrid
    or a SMTP server.
    """
    if conf.ON_HEROKU:
        send_sendgrid(**kwargs)
    else:
        send_smtp(**kwargs)

def send_smtp(to="", bcc="", subject="", plaintext="", html=""):
    """
    Send an email.
    """
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = conf.NOTIFICATION_EMAIL
    msg['To'] = to
    msg['BCC'] = bcc

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(plaintext, 'plain', 'utf-8')
    part2 = MIMEText(html, 'html', 'utf-8')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    try:
        s = smtplib.SMTP(conf.NOTIFICATION_HOST)
        s.login(conf.NOTIFICATION_USERNAME, conf.NOTIFICATION_PASSWORD)
    except Exception:
        logger.exception("send_smtp raised:")
    else:
        s.sendmail(conf.NOTIFICATION_EMAIL, msg['To'] + ", " + msg['BCC'], msg.as_string())
        s.quit()


def send_postmark(to="", bcc="", subject="", plaintext=""):
    """
    Send an email via Postmark. Used when the application is deployed on
    Heroku.
    Note: The Postmark team has chosen not to continue development of this
    Heroku add-on as of June 30, 2017. Newspipe is now using SendGrid when
    deployed on Heroku.
    """
    from postmark import PMMail
    try:
        message = PMMail(api_key = conf.POSTMARK_API_KEY,
                        subject = subject,
                        sender = conf.NOTIFICATION_EMAIL,
                        text_body = plaintext)
        message.to = to
        if bcc != "":
            message.bcc = bcc
        message.send()
    except Exception as e:
        logger.exception('send_postmark raised:')
        raise e


def send_sendgrid(to="", bcc="", subject="", plaintext=""):
    """
    Send an email via SendGrid. Used when the application is deployed on
    Heroku.
    """
    sg = sendgrid.SendGridAPIClient(apikey=conf.SENDGRID_API_KEY)
    from_email = Email(conf.NOTIFICATION_EMAIL)
    subject = subject
    to_email = Email(to)
    content = Content('text/plain', plaintext)
    mail = Mail(from_email, subject, to_email, content)
    if bcc != "":
        personalization = Personalization()
        personalization.add_bcc(Email(bcc))
        mail.add_personalization(personalization)
    response = sg.client.mail.send.post(request_body=mail.get())
    # print(response.status_code)
    # print(response.body)
    # print(response.headers)

#! /usr/bin/env python
# -*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2014  Cédric Bonhomme - http://cedricbonhomme.org/
#
# For more information : https://bitbucket.org/cedricbonhomme/pyaggr3g470r/
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

from postmark import PMMail

from pyaggr3g470r import utils
import conf
from pyaggr3g470r.decorators import async

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
    This functions enables to send email through Postmark
    or a SMTP server.
    """
    if conf.ON_HEROKU:
        send_postmark(to=kwargs.get("to"),
                      bcc=kwargs.get("bcc"),
                      subject=kwargs.get("subject"),
                      plaintext=kwargs.get("plaintext"))
    else:
        send_email(to=kwargs.get("to"),
                   bcc=kwargs.get("bcc"),
                   subject=kwargs.get("subject"),
                   plaintext=kwargs.get("plaintext"),
                   html=kwargs.get("html"))

def send_email(to="", bcc="", subject="", plaintext="", html=""):
    """
    Send an email.
    """
    # Create the body of the message (a plain-text and an HTML version).
    if plaintext == "":
        plaintext = utils.clear_string(html)

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
        logger.exception("send_email raised:")
    else:
        s.sendmail(conf.NOTIFICATION_EMAIL, msg['To'] + ", " + msg['BCC'], msg.as_string())
        s.quit()

def send_postmark(to="", bcc="", subject="", plaintext=""):
    """
    Send an email via Postmark. Used when the application is deployed on
    Heroku.
    """
    try:
        message = PMMail(api_key = conf.POSTMARK_API_KEY,
                        subject = subject,
                        sender = conf.NOTIFICATION_EMAIL,
                        text_body = plaintext)
        if bcc != "":
            message.to = conf.NOTIFICATION_EMAIL
            message.bcc = bcc
        elif bcc == "":
            message.to = recipients
        message.send()
    except Exception as e:
        logger.exception("send_postmark raised:")
        raise e


#
# Notifications
#
def information_message(subject, plaintext):
    """
    Send an information message to the users of the platform.
    """
    from pyaggr3g470r.models import User
    users = User.query.all()
    # Only send email for activated accounts.
    emails = [user.email for user in users if user.activation_key == ""]
    # Postmark has a limit of twenty recipients per message in total.
    for i in xrange(0, len(emails), 19):
        send(to=conf.NOTIFICATION_EMAIL, bcc=", ".join(emails[i:i+19]), subject=subject, plaintext=plaintext)

    #for user in users:
        #try:
            #send(user=user, subject=subject, plaintext=plaintext)
        #except:
            #continue

def new_account_notification(user):
    """
    Account creation notification.
    """
    plaintext = """Hello,\n\nYour account has been created. Click on the following link to confirm it:\n%s\n\nSee you,""" % \
                        (conf.PLATFORM_URL + 'confirm_account/' + user.activation_key)
    send(to=conf.NOTIFICATION_EMAIL, bcc=user.email, subject="[pyAggr3g470r] Account creation", plaintext=plaintext)

def new_account_activation(user):
    """
    Account activation notification.
    """
    plaintext = """Hello,\n\nYour account has been activated. You can now connect to the platform:\n%s\n\nSee you,""" % \
                        (conf.PLATFORM_URL)
    send(to=conf.NOTIFICATION_EMAIL, bcc=user.email, subject="[pyAggr3g470r] Account activated", plaintext=plaintext)

def new_password_notification(user, password):
    """
    New password notification.
    """
    plaintext = """Hello,\n\nA new password has been generated at your request:\n\n%s""" % \
                        (password, )
    plaintext += "\n\nIt is advised to replace it as soon as connected to pyAggr3g470r.\n\nSee you,"
    send(to=conf.NOTIFICATION_EMAIL, bcc=user.email, subject="[pyAggr3g470r]  New password", plaintext=plaintext)

def new_article_notification(user, feed, article):
    """
    New article notification.
    """
    subject = '[pyAggr3g470r] ' + feed.title + ": " + article.title
    html = """<html>\n<head>\n<title>%s</title>\n</head>\n<body>\n%s\n</body>\n</html>""" % \
                        (feed.title + ": " + article.title, article.content)
    plaintext = utils.clear_string(html)
    send(to=conf.NOTIFICATION_EMAIL, bcc=user.email, subject=subject, plaintext=plaintext, html=html)

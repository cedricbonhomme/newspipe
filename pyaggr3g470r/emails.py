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

def send_email(mfrom, mto, feed, article):
    """
    Send the article via mail.
    """
    # Create the body of the message (a plain-text and an HTML version).
    html = """<html>\n<head>\n<title>%s</title>\n</head>\n<body>\n%s\n</body>\n</html>""" % \
                (feed.title + ": " + article.title, article.content)
    text = utils.clear_string(article.content)

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '[pyAggr3g470r] ' + feed.title + ": " + article.title
    msg['From'] = mfrom
    msg['To'] = mto

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain', 'utf-8')
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
        s.sendmail(mfrom, mto, msg.as_string())
        s.quit()


#
# Notifications
#
def send_heroku(user=None, bcc="", subject="", plaintext=""):
    """
    Send an email on Heroku via Postmark.
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
            message.to = user.email
        message.send()
    except Exception as e:
        logger.exception("send_heroku raised:")
        raise e

def information_message(subject, plaintext):
    """
    Send an information message to the users of the platform.
    """
    from pyaggr3g470r.models import User
    users = User.query.all()
    emails = [user.email for user in users]
    if conf.ON_HEROKU:
        # Postmark has a limit of twenty recipients per message in total.
        #for i in xrange(0, len(emails), 20):
            #send_heroku(bcc=", ".join(emails[i:i+20]), subject=subject, plaintext=plaintext)
        for user in users:
            try:
                send_heroku(user=user, subject=subject, plaintext=plaintext)
            except:
                continue
    else:
        pass

def new_account_notification(user):
    """
    Account creation notification.
    """
    plaintext = """Hello,\n\nYour account has been created. Click on the following link to confirm it:\n%s\n\nSee you,""" % \
                        (conf.PLATFORM_URL + 'confirm_account/' + user.activation_key)
    if conf.ON_HEROKU:
        send_heroku(user=user, subject="[pyAggr3g470r] Account creation", plaintext=plaintext)
    else:
        pass

def new_account_activation(user):
    """
    Account activation notification.
    """
    plaintext = """Hello,\n\nYour account has been activated. You can now connect to the platform:\n%s\n\nSee you,""" % \
                        (conf.PLATFORM_URL)
    if conf.ON_HEROKU:
        send_heroku(user=user, subject="[pyAggr3g470r] Account activated", plaintext=plaintext)
    else:
        pass

def new_password_notification(user, password):
    """
    """
    plaintext = """Hello,\n\nA new password has been generated at your request:\n\n%s""" % \
                        (password, )
    plaintext += "\n\nIt is advised to replace it as soon as connected to pyAggr3g470r.\n\nSee you,"

    if conf.ON_HEROKU:
        send_heroku(user=user, subject="[pyAggr3g470r] New password", plaintext=plaintext)
    else:
        pass

def new_article_notification(user, feed, article):
    if conf.ON_HEROKU:
        pass
    else:
        send_email(conf.NOTIFICATION_EMAIL, user.email, feed, article)

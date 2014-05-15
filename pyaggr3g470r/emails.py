#! /usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from postmark import PMMail

import log
import utils
import conf
from decorators import async

pyaggr3g470r_log = log.Log("mail")

@async
def send_async_email(mfrom, mto, msg):
    try:
        s = smtplib.SMTP(conf.MAIL_HOST)
        s.login(conf.MAIL_USERNAME, conf.MAIL_PASSWORD)
    except Exception as e:
        pyaggr3g470r_log.error(str(e))
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
        s = smtplib.SMTP(conf.MAIL_HOST)
        s.login(conf.MAIL_USERNAME, conf.MAIL_PASSWORD)
    except Exception as e:
        pyaggr3g470r_log.error(str(e))
    else:
        s.sendmail(mfrom, mto, msg.as_string())
        s.quit()



#
# Notifications
#
def new_account_notification(user):
    if conf.ON_HEROKU:
        try:
            plaintext = """Hello,\n\nYour account has been created. Click on the following link to confirm it:\n%s\n\nSee you,""" % \
                        (conf.PLATFORM_URL + 'confirm_account/' + user.activation_key)

            message = PMMail(api_key = conf.POSTMARK_API_KEY,
                    subject = "[pyAggr3g470r] Account activation",
                    sender = conf.ADMIN_EMAIL,
                    to = user.email,
                    text_body = plaintext)

            message.send()
        except Exception as e:
            raise e
    else:
        pass

def new_account_activation(user):
    if conf.ON_HEROKU:
        try:
            plaintext = """Hello,\n\nYour account has been activated. You can now connect to the platform:\n%s\n\nSee you,""" % \
                        (conf.PLATFORM_URL)

            message = PMMail(api_key = conf.POSTMARK_API_KEY,
                    subject = "[pyAggr3g470r] Account activation",
                    sender = conf.ADMIN_EMAIL,
                    to = user.email,
                    text_body = plaintext)

            message.send()
        except Exception as e:
            raise e
    else:
        pass

def new_article_notification(user, feed, article):
    send_email(conf.ADMIN_EMAIL, user.email, feed, article)
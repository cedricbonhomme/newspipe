#! /usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

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
    try:
        html = """<html>\n<head>\n<title>[pyAggr3g470r] Account activation</title>\n</head>\n<body>\nYour account has been created. Clink on the following to confirm it:%s\n</body>\n</html>""" % \
                    (conf.PLATFORM_URL + 'confirm_account/' + user.activation_key)
        plaintext = utils.clear_string(html)
        
        r = requests.post("https://api.mailgun.net/v2/%s/messages" % conf.MAILGUN_DOMAIN,
                            auth=("api", conf.MAILGUN_KEY),
                            data={
                                "from": conf.ADMIN_EMAIL,
                                "to": user.email,
                                "subject": subject,
                                "text": plaintext,
                                "html": html
                            }
                        )
        return r
    except Exception as e:
        print str(e)
        

    
def new_article_notification(user, feed, article):
    send_email(conf.ADMIN_EMAIL, user.email, feed, article)
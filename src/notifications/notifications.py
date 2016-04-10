#! /usr/bin/env python
# -*- coding: utf-8 -*-

# JARR - A Web based news aggregator.
# Copyright (C) 2010-2016  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : https://github.com/JARR-aggregator/JARR/
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

import datetime
from flask import render_template
import conf
from notifications import emails
from web.lib.user_utils import generate_confirmation_token


def information_message(subject, plaintext):
    """
    Send an information message to the users of the platform.
    """
    from web.models import User
    users = User.query.all()
    # Only send email for activated accounts.
    user_emails = [user.email for user in users if user.enabled]
    # Postmark has a limit of twenty recipients per message in total.
    for i in xrange(0, len(user_emails), 19):
        emails.send(to=conf.NOTIFICATION_EMAIL,
                    bcc=", ".join(user_emails[i:i+19]),
                    subject=subject, plaintext=plaintext)

def new_account_notification(user):
    """
    Account creation notification.
    """
    token = generate_confirmation_token(user.email)
    expire_time = datetime.datetime.now() + \
                    datetime.timedelta(seconds=conf.TOKEN_VALIDITY_PERIOD)

    plaintext = render_template('emails/account_activation.txt',
                                    user=user, platform_url=conf.PLATFORM_URL,
                                    token=token,
                                    expire_time=expire_time)

    emails.send(to=user.email, bcc=conf.NOTIFICATION_EMAIL,
                subject="[JARR] Account creation", plaintext=plaintext)

def new_password_notification(user, password):
    """
    New password notification.
    """
    plaintext = render_template('emails/new_password.txt',
                                    user=user, password=password)
    emails.send(to=user.email,
                bcc=conf.NOTIFICATION_EMAIL,
                subject="[JARR] New password", plaintext=plaintext)

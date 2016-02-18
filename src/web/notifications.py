#! /usr/bin/env python
# -*- coding: utf-8 -*-

# jarr - A Web based news aggregator.
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

import conf
from web import emails
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
    plaintext = """Hello,\n\nYour account has been created. Click on the following link to confirm it:\n%s\n\nSee you,""" % \
                        (conf.PLATFORM_URL + 'user/confirm_account/' + token)
    emails.send(to=user.email, bcc=conf.NOTIFICATION_EMAIL,
                subject="[jarr] Account creation", plaintext=plaintext)

def new_account_activation(user):
    """
    Account activation notification.
    """
    plaintext = """Hello,\n\nYour account has been activated. You can now connect to the platform:\n%s\n\nSee you,""" % \
                        (conf.PLATFORM_URL)
    emails.send(to=user.email, bcc=conf.NOTIFICATION_EMAIL,
                subject="[jarr] Account activated", plaintext=plaintext)

def new_password_notification(user, password):
    """
    New password notification.
    """
    plaintext = """Hello,\n\nA new password has been generated at your request:\n\n%s""" % \
                        (password, )
    plaintext += "\n\nIt is advised to replace it as soon as connected to jarr.\n\nSee you,"
    emails.send(to=user.email,
                bcc=conf.NOTIFICATION_EMAIL,
                subject="[jarr]  New password", plaintext=plaintext)

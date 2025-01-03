#! /usr/bin/env python
# Newspipe - A web news aggregator.
# Copyright (C) 2010-2025 Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information: https://github.com/cedricbonhomme/newspipe
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

from newspipe.bootstrap import application
from newspipe.notifications import emails
from newspipe.web.lib.user_utils import generate_confirmation_token


def new_account_notification(user, email):
    """
    Account creation notification.
    """
    token = generate_confirmation_token(user.nickname)
    expire_time = datetime.datetime.now() + datetime.timedelta(
        seconds=application.config["TOKEN_VALIDITY_PERIOD"]
    )

    plaintext = render_template(
        "emails/account_activation.txt",
        user=user,
        platform_url=application.config["PLATFORM_URL"],
        token=token,
        expire_time=expire_time,
    )

    emails.send(
        to=email,
        subject="[Newspipe] Account creation",
        plaintext=plaintext,
    )


def new_password_notification(user, password):
    """
    New password notification.
    """
    plaintext = render_template("emails/new_password.txt", user=user, password=password)
    emails.send(
        to=user.email,
        subject="[Newspipe] New password",
        plaintext=plaintext,
    )

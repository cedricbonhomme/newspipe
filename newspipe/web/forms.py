#! /usr/bin/env python
# vim: set ts=4 sts=4 sw=4 et:
# Newspipe - A web news aggregator.
# Copyright (C) 2010-2024 Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information: https://github.com/cedricbonhomme/newspipe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.3 $"
__date__ = "$Date: 2013/11/05 $"
__revision__ = "$Date: 2015/05/06 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

import logging

from flask import redirect, url_for
from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from werkzeug.exceptions import NotFound
from wtforms import (
    BooleanField,
    HiddenField,
    PasswordField,
    SelectField,
    SelectMultipleField,
    SubmitField,
    TextAreaField,
    StringField,
    validators,
)
from wtforms.fields import EmailField, URLField

from newspipe.bootstrap import application
from newspipe.controllers import LdapuserController, UserController
from newspipe.lib import misc_utils
from newspipe.models import User

logger = logging.getLogger(__name__)


class SignupForm(FlaskForm):
    """
    Sign up form (registration to newspipe).
    """

    nickname = StringField(
        lazy_gettext("Nickname"),
        [validators.DataRequired(lazy_gettext("Please enter your nickname."))],
    )
    email = EmailField(
        lazy_gettext("Email"),
        [
            validators.Length(min=6, max=35),
            validators.DataRequired(
                lazy_gettext(
                    "Please enter your email address (only for account activation, won't be stored)."
                )
            ),
        ],
    )
    password = PasswordField(
        lazy_gettext("Password"),
        [
            validators.DataRequired(lazy_gettext("Please enter a password.")),
            validators.Length(min=20, max=500),
        ],
    )
    submit = SubmitField(lazy_gettext("Sign up"))

    def validate(self):
        ucontr = UserController()
        validated = super().validate()
        if ucontr.read(nickname=self.nickname.data).count():
            self.nickname.errors.append("Nickname already taken")
            validated = False
        if self.nickname.data != User.make_valid_nickname(self.nickname.data):
            self.nickname.errors.append(
                lazy_gettext(
                    "This nickname has invalid characters. "
                    "Please use letters, numbers, dash and underscores only."
                )
            )
            validated = False
        return validated


class RedirectForm(FlaskForm):
    """
    Secure back redirects with WTForms.
    """

    next = HiddenField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = misc_utils.get_redirect_target() or ""

    def redirect(self, endpoint="home", **values):
        url = misc_utils.is_safe_url(self.next.data)
        if url:
            return redirect(url)
        target = misc_utils.get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


class SigninForm(RedirectForm):
    """
    Sign in form (connection to newspipe).
    """

    nickmane = StringField(
        "Nickname",
        [
            validators.Length(min=3, max=35),
            validators.DataRequired(lazy_gettext("Please enter your nickname.")),
        ],
    )
    password = PasswordField(
        lazy_gettext("Password"),
        [
            validators.DataRequired(lazy_gettext("Please enter a password.")),
        ],
    )
    submit = SubmitField(lazy_gettext("Log In"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        validated = super().validate()
        # try ldap before doing anything else
        ldap_enabled = (
            application.config["LDAP_ENABLED"]
            if "LDAP_ENABLED" in application.config
            else False
        )
        ldapuser = None
        if ldap_enabled:
            ucontrldap = LdapuserController()
            try:
                # this returns False if invalid username or password.
                ldapuser = ucontrldap.check_password(
                    user=self.nickmane.data,
                    password=self.password.data,
                    config=application.config,
                )
                if ldapuser:
                    self.nickmane.errors.append(
                        f"validated ldap user {self.nickmane.data}"
                    )
                else:
                    # self.nickmane.errors.append(f"Invalid username or password.")
                    raise NotFound
            except NotFound:
                pass  # just assume the user is trying a local account
        ucontr = UserController()
        try:
            user = ucontr.get(nickname=self.nickmane.data)
        except NotFound:
            if ldap_enabled and ldapuser:
                try:
                    user = ucontr.create(
                        nickname=self.nickmane.data,
                        password="",
                        automatic_crawling=True,
                        is_admin=False,
                        is_active=True,
                        external_auth="ldap",
                    )
                    if user:
                        validated = True
                        self.user = user
                except Exception:
                    self.nickmane.errors.append(
                        f"Unable to provision user for valid ldap user {self.nickmane.data}"
                    )
                    validated = False
            else:
                self.nickmane.errors.append("Wrong nickname")
                validated = False
        else:
            if not user.is_active:
                self.nickmane.errors.append("Account not active")
                validated = False
            # must short-circuit the password check for ldap users
            if not ldapuser:
                try:
                    # with an external_auth user but external auth disabled in config now,
                    # the empty password on the user in the database will fail
                    if not ucontr.check_password(user, self.password.data):
                        self.password.errors.append("Wrong password")
                        validated = False
                except AttributeError:
                    if ldap_enabled:
                        self.password.errors.append("Wrong password")
                        validated = False
                    else:
                        self.password.errors.append(
                            "External auth {user.external_auth} unavailable. Contact the admin."
                        )
                        validated = False
            self.user = user
        return validated


class UserForm(FlaskForm):
    """
    Create or edit a user (for the administrator).
    """

    nickname = StringField(
        lazy_gettext("Nickname"),
        [validators.DataRequired(lazy_gettext("Please enter your nickname."))],
    )
    password = PasswordField(lazy_gettext("Password"))
    automatic_crawling = BooleanField(lazy_gettext("Automatic crawling"), default=True)
    submit = SubmitField(lazy_gettext("Save"))

    def validate(self):
        validated = super().validate()
        if self.nickname.data != User.make_valid_nickname(self.nickname.data):
            self.nickname.errors.append(
                lazy_gettext(
                    "This nickname has invalid characters. "
                    "Please use letters, numbers, dots and underscores only."
                )
            )
            validated = False
        return validated


class ProfileForm(FlaskForm):
    """
    Edit user information.
    """

    nickname = StringField(
        lazy_gettext("Nickname"),
        # [validators.Required(lazy_gettext("Please enter your nickname."))],
        [validators.Optional()],
    )
    password = PasswordField(lazy_gettext("Password"))
    password_conf = PasswordField(lazy_gettext("Password"))
    automatic_crawling = BooleanField(lazy_gettext("Automatic crawling"), default=True)
    bio = TextAreaField(lazy_gettext("Bio"))
    webpage = URLField(lazy_gettext("Webpage"))
    mastodon = StringField(
        "Mastodon", default="", validators=[validators.Length(min=0, max=100)]
    )
    github = StringField(
        "GitHub username", default="", validators=[validators.Length(min=0, max=39)]
    )
    linkedin = StringField(
        "LinkedIn username", default="", validators=[validators.Length(min=0, max=30)]
    )
    is_public_profile = BooleanField(lazy_gettext("Public profile"), default=True)
    submit = SubmitField(lazy_gettext("Save"))

    def validate(self):
        validated = super().validate()
        if self.password.data:
            if self.password.data != self.password_conf.data:
                message = lazy_gettext("Passwords aren't the same.")
                self.password.errors.append(message)
                self.password_conf.errors.append(message)
                validated = False
            if not 20 <= len(self.password.data) <= 500:
                message = lazy_gettext(
                    "Password must be between 20 and 500 characters."
                )
                self.password.errors.append(message)
                validated = False
        if self.nickname.data and (
            self.nickname.data != User.make_valid_nickname(self.nickname.data)
        ):
            self.nickname.errors.append(
                lazy_gettext(
                    "This nickname has "
                    "invalid characters. Please use letters, numbers, dots and"
                    " underscores only."
                )
            )
            validated = False
        return validated


class AddFeedForm(FlaskForm):
    title = StringField(lazy_gettext("Title"), [validators.Optional()])
    link = StringField(lazy_gettext("Feed link"))
    site_link = StringField(lazy_gettext("Site link"))
    description = StringField(lazy_gettext("Description"))
    enabled = BooleanField(lazy_gettext("Check for updates"), default=True)
    submit = SubmitField(lazy_gettext("Save"))
    category_id = SelectField(
        lazy_gettext("Category of the feed"), [validators.Optional()]
    )
    private = BooleanField(lazy_gettext("Private"), default=False)

    def set_category_choices(self, categories):
        self.category_id.choices = [("0", "No Category")]
        self.category_id.choices += [(str(cat.id), cat.name) for cat in categories]


class CategoryForm(FlaskForm):
    name = StringField(
        lazy_gettext("Category name"),
        [
            validators.Length(min=2, max=30),
            validators.InputRequired("Please enter a category name."),
        ],
    )
    feeds = SelectMultipleField(lazy_gettext("Feeds in this category"), coerce=int)
    submit = SubmitField(lazy_gettext("Save"))

    def set_feed_choices(self, feeds):
        self.feeds.choices = []
        self.feeds.choices += [(feed.id, feed.title) for feed in feeds]


class BookmarkForm(FlaskForm):
    href = StringField(
        lazy_gettext("URL"),
        [validators.DataRequired(lazy_gettext("Please enter an URL."))],
    )
    title = StringField(lazy_gettext("Title"), [validators.Length(min=0, max=100)])
    description = StringField(
        lazy_gettext("Description"), [validators.Length(min=0, max=500)]
    )
    tags = StringField(lazy_gettext("Tags"))
    to_read = BooleanField(lazy_gettext("To read"), default=False)
    shared = BooleanField(lazy_gettext("Shared"), default=True)
    submit = SubmitField(lazy_gettext("Save"))


class InformationMessageForm(FlaskForm):
    subject = StringField(
        lazy_gettext("Subject"),
        [validators.DataRequired(lazy_gettext("Please enter a subject."))],
    )
    message = TextAreaField(
        lazy_gettext("Message"),
        [validators.DataRequired(lazy_gettext("Please enter a content."))],
    )
    submit = SubmitField(lazy_gettext("Send"))

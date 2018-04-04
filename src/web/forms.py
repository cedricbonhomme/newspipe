#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Newspipe - A Web based news aggregator.
# Copyright (C) 2010-2016  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : http://github.com/Newspipe/Newspipe
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

from flask import flash, url_for, redirect
from flask_wtf import Form
from flask_babel import lazy_gettext
from werkzeug.exceptions import NotFound
from wtforms import TextField, TextAreaField, PasswordField, BooleanField, \
        SubmitField, IntegerField, SelectField, validators, HiddenField
from wtforms.fields.html5 import EmailField, URLField

from lib import misc_utils
from web.controllers import UserController
from web.models import User


class SignupForm(Form):
    """
    Sign up form (registration to newspipe).
    """
    nickname = TextField(lazy_gettext("Nickname"),
            [validators.Required(lazy_gettext("Please enter your nickname."))])
    email = EmailField(lazy_gettext("Email"),
            [validators.Length(min=6, max=35),
             validators.Required(
                 lazy_gettext("Please enter your email address (only for account activation, won't be stored)."))])
    password = PasswordField(lazy_gettext("Password"),
            [validators.Required(lazy_gettext("Please enter a password.")),
             validators.Length(min=6, max=100)])
    submit = SubmitField(lazy_gettext("Sign up"))

    def validate(self):
        ucontr = UserController()
        validated = super().validate()
        if ucontr.read(nickname=self.nickname.data).count():
            self.nickname.errors.append('Nickname already taken')
            validated = False
        return validated


class RedirectForm(Form):
    """
    Secure back redirects with WTForms.
    """
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = misc_utils.get_redirect_target() or ''

    def redirect(self, endpoint='home', **values):
        if misc_utils.is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = misc_utils.get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


class SigninForm(RedirectForm):
    """
    Sign in form (connection to newspipe).
    """
    nickmane = TextField("Nickname",
                [validators.Length(min=3, max=35),
                validators.Required(
                lazy_gettext("Please enter your nickname."))])
    password = PasswordField(lazy_gettext('Password'),
            [validators.Required(lazy_gettext("Please enter a password.")),
             validators.Length(min=6, max=100)])
    submit = SubmitField(lazy_gettext("Log In"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        validated = super().validate()
        ucontr = UserController()
        try:
            user = ucontr.get(nickname=self.nickmane.data)
        except NotFound:
            self.nickmane.errors.append(
                'Wrong nickname')
            validated = False
        else:
            if not user.is_active:
                self.nickmane.errors.append('Account not active')
                validated = False
            if not ucontr.check_password(user, self.password.data):
                self.password.errors.append('Wrong password')
                validated = False
            self.user = user
        return validated


class UserForm(Form):
    """
    Create or edit a user (for the administrator).
    """
    nickname = TextField(lazy_gettext("Nickname"),
            [validators.Required(lazy_gettext("Please enter your nickname."))])
    password = PasswordField(lazy_gettext("Password"))
    automatic_crawling = BooleanField(lazy_gettext("Automatic crawling"),
                                default=True)
    submit = SubmitField(lazy_gettext("Save"))

    def validate(self):
        validated = super(UserForm, self).validate()
        if self.nickname.data != User.make_valid_nickname(self.nickname.data):
            self.nickname.errors.append(lazy_gettext(
                    'This nickname has invalid characters. '
                    'Please use letters, numbers, dots and underscores only.'))
            validated = False
        return validated


class ProfileForm(Form):
    """
    Edit user information.
    """
    nickname = TextField(lazy_gettext("Nickname"),
            [validators.Required(lazy_gettext("Please enter your nickname."))])
    password = PasswordField(lazy_gettext("Password"))
    password_conf = PasswordField(lazy_gettext("Password Confirmation"))
    automatic_crawling = BooleanField(lazy_gettext("Automatic crawling"),
                                default=True)
    bio = TextAreaField(lazy_gettext("Bio"))
    webpage = URLField(lazy_gettext("Webpage"))
    twitter = URLField(lazy_gettext("Twitter"))
    is_public_profile = BooleanField(lazy_gettext("Public profile"),
                                default=True)
    submit = SubmitField(lazy_gettext("Save"))

    def validate(self):
        validated = super(ProfileForm, self).validate()
        if self.password.data != self.password_conf.data:
            message = lazy_gettext("Passwords aren't the same.")
            self.password.errors.append(message)
            self.password_conf.errors.append(message)
            validated = False
        if self.nickname.data != User.make_valid_nickname(self.nickname.data):
            self.nickname.errors.append(lazy_gettext('This nickname has '
                    'invalid characters. Please use letters, numbers, dots and'
                    ' underscores only.'))
            validated = False
        return validated


class AddFeedForm(Form):
    title = TextField(lazy_gettext("Title"), [validators.Optional()])
    link = TextField(lazy_gettext("Feed link"),
            [validators.Required(lazy_gettext("Please enter the URL."))])
    site_link = TextField(lazy_gettext("Site link"), [validators.Optional()])
    enabled = BooleanField(lazy_gettext("Check for updates"), default=True)
    submit = SubmitField(lazy_gettext("Save"))
    category_id = SelectField(lazy_gettext("Category of the feed"),
                              [validators.Optional()])
    private = BooleanField(lazy_gettext("Private"), default=False)

    def set_category_choices(self, categories):
        self.category_id.choices = [('0', 'No Category')]
        self.category_id.choices += [(str(cat.id), cat.name)
                                      for cat in categories]


class CategoryForm(Form):
    name = TextField(lazy_gettext("Category name"))
    submit = SubmitField(lazy_gettext("Save"))


class BookmarkForm(Form):
    href = TextField(lazy_gettext("URL"),
                            [validators.Required(
                                        lazy_gettext("Please enter an URL."))])
    title = TextField(lazy_gettext("Title"),
                            [validators.Length(min=0, max=100)])
    description = TextField(lazy_gettext("Description"),
                            [validators.Length(min=0, max=500)])
    tags = TextField(lazy_gettext("Tags"))
    to_read = BooleanField(lazy_gettext("To read"), default=False)
    shared = BooleanField(lazy_gettext("Shared"), default=False)
    submit = SubmitField(lazy_gettext("Save"))


class InformationMessageForm(Form):
    subject = TextField(lazy_gettext("Subject"),
            [validators.Required(lazy_gettext("Please enter a subject."))])
    message = TextAreaField(lazy_gettext("Message"),
            [validators.Required(lazy_gettext("Please enter a content."))])
    submit = SubmitField(lazy_gettext("Send"))


class RecoverPasswordForm(Form):
    email = EmailField(lazy_gettext("Email"),
            [validators.Length(min=6, max=35),
             validators.Required(
                 lazy_gettext("Please enter your email address."))])
    submit = SubmitField(lazy_gettext("Recover"))

    def validate(self):
        if not super(RecoverPasswordForm, self).validate():
            return False

        user = User.query.filter(User.email == self.email.data).first()
        if user and user.enabled:
            return True
        elif user and not user.enabled:
            flash(lazy_gettext('Account not confirmed.'), 'danger')
            return False
        else:
            flash(lazy_gettext('Invalid email.'), 'danger')
            return False

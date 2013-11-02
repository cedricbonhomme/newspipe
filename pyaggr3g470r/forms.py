#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, PasswordField, SubmitField, validators

import models

class SigninForm(Form):
    email = TextField("Email", [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
    password = PasswordField('Password', [validators.Required("Please enter a password.")])
    submit = SubmitField("Log In")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

        user = models.User.objects(email = self.email.data).first()
        if user and user.check_password(self.password.data):
            return True
        else:
            self.email.errors.append("Invalid e-mail or password")
            return False

class AddFeedForm(Form):
    title = TextField("Title", [validators.Required("Please enter a title.")])
    link = TextField("Feed link", [validators.Required("Please enter a link.")])
    site_link = TextField("Site link", [validators.Required("Please enter a site URL.")])
    submit = SubmitField("Add feed")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        return True
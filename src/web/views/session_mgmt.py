#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
import logging

from flask import (render_template, flash, session, request,
                   url_for, redirect, current_app)
from flask.ext.babel import gettext
from flask.ext.login import LoginManager, logout_user, \
                            login_required, current_user
from flask.ext.principal import (Principal, AnonymousIdentity, UserNeed,
                                 identity_changed, identity_loaded,
                                 session_identity_loader)
from werkzeug import generate_password_hash
from sqlalchemy.exc import IntegrityError

import conf
from web.views.common import admin_role, api_role, login_user_bundle
from web.controllers import UserController
from web.forms import SignupForm, SigninForm

Principal(current_app)
# Create a permission with a single Need, in this case a RoleNeed.

login_manager = LoginManager()
login_manager.init_app(current_app)
login_manager.login_view = 'login'

logger = logging.getLogger(__name__)


@identity_loaded.connect_via(current_app._get_current_object())
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if current_user.is_authenticated:
        identity.provides.add(UserNeed(current_user.id))
        if current_user.is_admin:
            identity.provides.add(admin_role)
        #if current_user.is_api:
            #identity.provides.add(api_role)

@login_manager.user_loader
def load_user(id):
    # Return an instance of the User model
    return UserController().get(id=id)

"""@current_app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.utcnow()
        db.session.add(current_user)
        db.session.commit()"""

@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SigninForm()
    if form.validate_on_submit():
        login_user_bundle(form.user)
        return form.redirect('home')
    return render_template('login.html', form=form)

@current_app.route('/logout')
@login_required
def logout():
    # Remove the user information from the session
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app, identity=AnonymousIdentity())
    session_identity_loader()

    return redirect(url_for('login'))

@current_app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Signup page.
    """
    if not conf.SELF_REGISTRATION:
        flash(gettext("Self-registration is disabled."), 'warning')
        return redirect(url_for('home'))
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('home'))

    form = SignupForm()

    if form.validate_on_submit():
        role_user = Role.query.filter(Role.name == "user").first()
        user = User(nickname=form.nickname.data,
                    email=form.email.data,
                    pwdhash=generate_password_hash(form.password.data))
        user.roles = [role_user]
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            flash(gettext('Email already used.'), 'warning')
            return render_template('signup.html', form=form)

        # Send the confirmation email
        try:
            notifications.new_account_notification(user)
        except Exception as error:
            flash(gettext('Problem while sending activation email: %(error)s',
                          error=error), 'danger')
            return redirect(url_for('home'))

        flash(gettext('Your account has been created. '
                      'Check your mail to confirm it.'), 'success')
        return redirect(url_for('home'))

    return render_template('signup.html', form=form)

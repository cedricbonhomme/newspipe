#! /usr/bin/env python
# -*- coding: utf-8 -*-

# JARR - A Web based news aggregator.
# Copyright (C) 2010-2016  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : https://github.com/JARR-aggregator/JARR
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

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2010/02/28 $"
__revision__ = "$Date: 2014/02/28 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "AGPLv3"

from flask import (Blueprint, g, render_template, redirect,
                   flash, url_for, request)
from flask.ext.babel import gettext
from flask.ext.login import login_required, current_user

from flask.ext.principal import Permission, RoleNeed

from web.lib.utils import redirect_url
from web.models import Role
from web.controllers import UserController, ArticleController

from web.forms import InformationMessageForm, UserForm
from web import notifications

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
admin_permission = Permission(RoleNeed('admin'))


@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def dashboard():
    """
    Adminstrator's dashboard.
    """
    form = InformationMessageForm()

    if request.method == 'POST':
        if form.validate():
            try:
                notifications.information_message(form.subject.data,
                                                  form.message.data)
            except Exception as error:
                flash(gettext(
                        'Problem while sending email: %(error)s', error=error),
                        'danger')

    users = UserController().read()
    return render_template('admin/dashboard.html',
                           users=users, current_user=current_user, form=form)


@admin_bp.route('/user/create', methods=['GET'])
@admin_bp.route('/user/edit/<int:user_id>', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def user_form(user_id=None):
    if user_id is not None:
        user = UserController().get(id=user_id)
        form = UserForm(obj=user)
        message = gettext('Edit the user <i>%(nick)s</i>', nick=user.nickname)
    else:
        form = UserForm()
        message = gettext('Add a new user')
    return render_template('/admin/create_user.html',
                           form=form, message=message)


@admin_bp.route('/user/create', methods=['POST'])
@admin_bp.route('/user/edit/<int:user_id>', methods=['POST'])
@login_required
@admin_permission.require(http_exception=403)
def process_user_form(user_id=None):
    """
    Create or edit a user.
    """
    form = UserForm()
    user_contr = UserController()

    if not form.validate():
        return render_template('/admin/create_user.html', form=form,
                               message=gettext('Some errors were found'))

    role_user = Role.query.filter(Role.name == "user").first()
    if user_id is not None:
        # Edit a user
        user_contr.update({'id': user_id},
                          {'nickname': form.nickname.data,
                           'email': form.email.data,
                           'password': form.password.data,
                           'refresh_rate': form.refresh_rate.data})
        user = user_contr.get(id=user_id)
        flash(gettext('User %(nick)s successfully updated',
                      nick=user.nickname), 'success')
    else:
        # Create a new user (by the admin)
        user = user_contr.create(nickname=form.nickname.data,
                                 email=form.email.data,
                                 password=form.password.data,
                                 roles=[role_user],
                                 refresh_rate=form.refresh_rate.data,
                                 enabled=True)
        flash(gettext('User %(nick)s successfully created',
                      nick=user.nickname), 'success')
    return redirect(url_for('admin.user_form', user_id=user.id))


@admin_bp.route('/user/<int:user_id>', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def user(user_id=None):
    """
    See information about a user (stations, etc.).
    """
    user = UserController().get(id=user_id)
    if user is not None:
        article_contr = ArticleController(user_id)
        return render_template('/admin/user.html', user=user, feeds=user.feeds,
                article_count=article_contr.count_by_feed(),
                unread_article_count=article_contr.count_by_feed(readed=False))

    else:
        flash(gettext('This user does not exist.'), 'danger')
        return redirect(redirect_url())


@admin_bp.route('/delete_user/<int:user_id>', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def delete_user(user_id=None):
    """
    Delete a user (with all its data).
    """
    try:
        user = UserController().delete(user_id)
        flash(gettext('User %(nick)s successfully deleted',
                      nick=user.nickname), 'success')
    except Exception as error:
        flash(gettext('An error occured while trying to delete a user: '
                      '%(error)', error=error), 'danger')
    return redirect(redirect_url())

@admin_bp.route('/toggle_user/<int:user_id>', methods=['GET'])
@login_required
@admin_permission.require()
def toggle_user(user_id=None):
    """
    Enable or disable the account of a user.
    """
    user_contr = UserController()
    user = user_contr.get(id=user_id)

    if user is None:
        flash(gettext('This user does not exist.'), 'danger')
        return redirect(url_for('admin.dashboard'))

    user_contr.update({'id': user.id}, {'enabled': not user.enabled})
    flash(gettext('Account of the user %(nick)s successfully '
                         'updated.', nick=user.nickname), 'success')
    return redirect(url_for('admin.dashboard'))

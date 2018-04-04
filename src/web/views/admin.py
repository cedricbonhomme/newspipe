from datetime import datetime
from flask import (Blueprint, render_template, redirect, flash, url_for)
from flask_babel import gettext, format_timedelta
from flask_login import login_required, current_user
from werkzeug import generate_password_hash

from lib.utils import redirect_url
from web.views.common import admin_permission
from web.controllers import UserController
from web.forms import InformationMessageForm, UserForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def dashboard():
    last_cons, now = {}, datetime.utcnow()
    users = list(UserController().read().order_by('id'))
    form = InformationMessageForm()
    for user in users:
        last_cons[user.id] = format_timedelta(now - user.last_seen)
    return render_template('admin/dashboard.html', now=datetime.utcnow(),
            last_cons=last_cons, users=users, current_user=current_user,
            form=form)


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

    if user_id is not None:
        # Edit a user
        user_contr.update({'id': user_id},
                          {'nickname': form.nickname.data,
                           'password': form.password.data,
                           'automatic_crawling': form.automatic_crawling.data})
        user = user_contr.get(id=user_id)
        flash(gettext('User %(nick)s successfully updated',
                      nick=user.nickname), 'success')
    else:
        # Create a new user (by the admin)
        user = user_contr.create(nickname=form.nickname.data,
                            pwdhash=generate_password_hash(form.password.data),
                            automatic_crawling=form.automatic_crawling.data,
                            is_admin=False,
                            is_active=True)
        flash(gettext('User %(nick)s successfully created',
                      nick=user.nickname), 'success')
    return redirect(url_for('admin.user_form', user_id=user.id))


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
        flash(
            gettext('An error occurred while trying to delete a user: %(error)s',
                        error=error), 'danger')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/toggle_user/<int:user_id>', methods=['GET'])
@login_required
@admin_permission.require()
def toggle_user(user_id=None):
    """
    Enable or disable the account of a user.
    """
    ucontr = UserController()
    user = ucontr.get(id=user_id)
    user_changed = ucontr.update({'id': user_id},
            {'is_active': not user.is_active})

    if not user_changed:
        flash(gettext('This user does not exist.'), 'danger')
        return redirect(url_for('admin.dashboard'))

    else:
        act_txt = 'activated' if user.is_active else 'desactivated'
        message = gettext('User %(nickname)s successfully %(is_active)s',
                          nickname=user.nickname, is_active=act_txt)
    flash(message, 'success')
    return redirect(url_for('admin.dashboard'))

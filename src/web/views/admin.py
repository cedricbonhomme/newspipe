from datetime import datetime
from flask import (Blueprint, render_template, redirect, flash, url_for)
from flask.ext.babel import gettext, format_timedelta
from flask.ext.login import login_required, current_user

from web.views.common import admin_permission
from web.lib.utils import redirect_url
from web.controllers import UserController, ArticleController

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@admin_permission.require(http_exception=403)
def dashboard():
    last_cons, now = {}, datetime.utcnow()
    users = list(UserController().read().order_by('id'))
    for user in users:
        last_cons[user.id] = format_timedelta(now - user.last_connection)
    return render_template('admin/dashboard.html', now=datetime.utcnow(),
            last_cons=last_cons, users=users, current_user=current_user)


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
        message = gettext('User %(login)s successfully %(is_active)s',
                          login=user.login, is_active=act_txt)
    flash(message, 'success')
    return redirect(url_for('admin.dashboard'))

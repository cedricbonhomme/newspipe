import string
import random
from datetime import datetime, timedelta
from flask import (Blueprint, g, render_template, redirect,
                   flash, url_for, request)
from flask_babel import gettext
from flask_login import login_required, current_user

import conf
from notifications import notifications
from lib import misc_utils
from lib.data import import_opml, import_json
from web.lib.user_utils import confirm_token
from web.controllers import (UserController, FeedController, ArticleController,
                            CategoryController, BookmarkController)

from web.forms import ProfileForm, RecoverPasswordForm

users_bp = Blueprint('users', __name__, url_prefix='/users')
user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/<string:nickname>', methods=['GET'])
def profile_public(nickname=None):
    """
    Display the public profile of the user.
    """
    user_contr = UserController()
    user = user_contr.get(nickname=nickname)
    if not user.is_public_profile:
        if current_user.is_authenticated and current_user.id == user.id:
            flash(gettext('You must set your profile to public.'), 'info')
        return redirect(url_for('user.profile'))

    filters = {}
    filters['private'] = False
    feeds = FeedController(user.id).read(**filters).all()

    """word_size = 6
    filters = {}
    filters['retrieved_date__gt'] = datetime.now() - timedelta(weeks=10)
    articles = ArticleController(user.id).read(**filters).all()
    top_words = misc_utils.top_words(articles, n=50, size=int(word_size))
    tag_cloud = misc_utils.tag_cloud(top_words)"""

    return render_template('profile_public.html', user=user, feeds=feeds)


@user_bp.route('/management', methods=['GET', 'POST'])
@login_required
def management():
    """
    Display the management page.
    """
    if request.method == 'POST':
        if None != request.files.get('opmlfile', None):
            # Import an OPML file
            data = request.files.get('opmlfile', None)
            if not misc_utils.allowed_file(data.filename):
                flash(gettext('File not allowed.'), 'danger')
            else:
                try:
                    nb = import_opml(current_user.nickname, data.read())
                    if conf.CRAWLING_METHOD == "classic":
                        misc_utils.fetch(current_user.id, None)
                        flash(str(nb) + '  ' + gettext('feeds imported.'),
                                "success")
                        flash(gettext("Downloading articles..."), 'info')
                except:
                    flash(gettext("Impossible to import the new feeds."),
                            "danger")
        elif None != request.files.get('jsonfile', None):
            # Import an account
            data = request.files.get('jsonfile', None)
            if not misc_utils.allowed_file(data.filename):
                flash(gettext('File not allowed.'), 'danger')
            else:
                try:
                    nb = import_json(current_user.nickname, data.read())
                    flash(gettext('Account imported.'), "success")
                except:
                    flash(gettext("Impossible to import the account."),
                            "danger")
        else:
            flash(gettext('File not allowed.'), 'danger')

    nb_feeds = FeedController(current_user.id).read().count()
    art_contr = ArticleController(current_user.id)
    nb_articles = art_contr.read().count()
    nb_unread_articles = art_contr.read(readed=False).count()
    nb_categories = CategoryController(current_user.id).read().count()
    nb_bookmarks = BookmarkController(current_user.id).read().count()
    return render_template('management.html', user=current_user,
                            nb_feeds=nb_feeds, nb_articles=nb_articles,
                            nb_unread_articles=nb_unread_articles,
                            nb_categories=nb_categories,
                            nb_bookmarks=nb_bookmarks)


@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Edit the profile of the currently logged user.
    """
    user_contr = UserController(current_user.id)
    user = user_contr.get(id=current_user.id)
    form = ProfileForm()

    if request.method == 'POST':
        if form.validate():
            try:
                user_contr.update({'id': current_user.id},
                        {'nickname': form.nickname.data,
                        'password': form.password.data,
                        'automatic_crawling': form.automatic_crawling.data,
                        'is_public_profile': form.is_public_profile.data,
                        'bio': form.bio.data,
                        'webpage': form.webpage.data,
                        'twitter': form.twitter.data})
            except Exception as error:
                flash(gettext('Problem while updating your profile: '
                              '%(error)s', error=error), 'danger')
            else:
                flash(gettext('User %(nick)s successfully updated',
                          nick=user.nickname), 'success')
            return redirect(url_for('user.profile'))
        else:
            return render_template('profile.html', user=user, form=form)

    if request.method == 'GET':
        form = ProfileForm(obj=user)
        return render_template('profile.html', user=user, form=form)


@user_bp.route('/delete_account', methods=['GET'])
@login_required
def delete_account():
    """
    Delete the account of the user (with all its data).
    """
    UserController(current_user.id).delete(current_user.id)
    flash(gettext('Your account has been deleted.'), 'success')
    return redirect(url_for('login'))


@user_bp.route('/confirm_account/<string:token>', methods=['GET'])
def confirm_account(token=None):
    """
    Confirm the account of a user.
    """
    user_contr = UserController()
    user, nickname = None, None
    if token != "":
        nickname = confirm_token(token)
    if nickname:
        user = user_contr.read(nickname=nickname).first()
    if user is not None:
        user_contr.update({'id': user.id}, {'is_active': True})
        flash(gettext('Your account has been confirmed.'), 'success')
    else:
        flash(gettext('Impossible to confirm this account.'), 'danger')
    return redirect(url_for('login'))


# @user_bp.route('/recover', methods=['GET', 'POST'])
# def recover():
#     """
#     Enables the user to recover its account when he has forgotten
#     its password.
#     """
#     form = RecoverPasswordForm()
#     user_contr = UserController()
#
#     if request.method == 'POST':
#         if form.validate():
#             user = user_contr.get(email=form.email.data)
#             characters = string.ascii_letters + string.digits
#             password = "".join(random.choice(characters)
#                                for x in range(random.randint(8, 16)))
#             user.set_password(password)
#             user_contr.update({'id': user.id}, {'password': password})
#
#             # Send the confirmation email
#             try:
#                 notifications.new_password_notification(user, password)
#                 flash(gettext('New password sent to your address.'), 'success')
#             except Exception as error:
#                 flash(gettext('Problem while sending your new password: '
#                               '%(error)s', error=error), 'danger')
#
#             return redirect(url_for('login'))
#         return render_template('recover.html', form=form)
#
#     if request.method == 'GET':
#         return render_template('recover.html', form=form)

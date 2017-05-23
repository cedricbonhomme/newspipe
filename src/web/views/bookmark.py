import logging
from werkzeug.exceptions import BadRequest

from flask import Blueprint, render_template, flash, \
                  redirect, request, url_for
from flask_babel import gettext
from flask_login import login_required, current_user

import conf
from bootstrap import db
from web.forms import BookmarkForm
from web.controllers import BookmarkController, BookmarkTagController

logger = logging.getLogger(__name__)
bookmarks_bp = Blueprint('bookmarks', __name__, url_prefix='/bookmarks')
bookmark_bp = Blueprint('bookmark', __name__, url_prefix='/bookmark')


@bookmarks_bp.route('/', methods=['GET'])
@login_required
def list():
    "Lists the bookmarks."
    bookmark_contr = BookmarkController(current_user.id)
    return render_template('bookmarks.html',
        bookmarks=BookmarkController(current_user.id).read().order_by('time'))


@bookmark_bp.route('/create', methods=['GET'])
@bookmark_bp.route('/edit/<int:bookmark_id>', methods=['GET'])
@login_required
def form(bookmark_id=None):
    action = gettext("Add a bookmark")
    head_titles = [action]
    if bookmark_id is None:
        return render_template('edit_bookmark.html', action=action,
                               head_titles=head_titles, form=BookmarkForm())
    bookmark = BookmarkController(current_user.id).get(id=bookmark_id)
    action = gettext('Edit bookmark')
    head_titles = [action]
    form = BookmarkForm(obj=bookmark)
    form.tags.data = bookmark.tags_proxy
    return render_template('edit_bookmark.html', action=action,
                           head_titles=head_titles, bookmark=bookmark,
                           form=form)


@bookmark_bp.route('/create', methods=['POST'])
@bookmark_bp.route('/edit/<int:bookmark_id>', methods=['POST'])
@login_required
def process_form(bookmark_id=None):
    form = BookmarkForm()
    bookmark_contr = BookmarkController(current_user.id)
    tag_contr = BookmarkTagController(current_user.id)

    if not form.validate():
        return render_template('edit_bookmark.html', form=form)

    tags = []
    for tag in form.tags.data.split(','):
        new_tag = tag_contr.create(text= tag.strip(), user_id= current_user.id)
        tags.append(new_tag)

    bookmark_attr = {'href': form.href.data,
                    'description': form.description.data,
                    'title': form.title.data,
                    'tags': tags,
                    'shared': form.shared.data,
                    'to_read': form.to_read.data}

    if bookmark_id is not None:
        bookmark_contr.update({'id': bookmark_id}, bookmark_attr)
        flash(gettext('Bookmark successfully updated.'), 'success')
        return redirect(url_for('bookmark.form', bookmark_id=bookmark_id))

    # Create a new bookmark
    new_bookmark = bookmark_contr.create(**bookmark_attr)

    flash(gettext('Bookmark successfully created.'), 'success')

    return redirect(url_for('bookmark.form', bookmark_id=new_bookmark.id))

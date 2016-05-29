import logging
from flask import (request, render_template, flash,
                   url_for, redirect, current_app)
from flask_babel import gettext

from conf import API_ROOT
from web.lib.view_utils import etag_match

logger = logging.getLogger(__name__)


@current_app.errorhandler(401)
def authentication_required(error):
    if API_ROOT in request.url:
        return error
    flash(gettext('Authentication required.'), 'info')
    return redirect(url_for('login'))


@current_app.errorhandler(403)
def authentication_failed(error):
    if API_ROOT in request.url:
        return error
    flash(gettext('Forbidden.'), 'danger')
    return redirect(url_for('login'))


@current_app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@current_app.errorhandler(500)
def internal_server_error(error):
    return render_template('errors/500.html'), 500


@current_app.errorhandler(AssertionError)
def handle_sqlalchemy_assertion_error(error):
    return error.args[0], 400


@current_app.route('/about', methods=['GET'])
@etag_match
def about():
    return render_template('about.html')

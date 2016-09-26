import logging
import operator
from datetime import datetime, timedelta
from flask import (request, render_template, flash,
                   url_for, redirect, current_app)
from flask_babel import gettext
from sqlalchemy import desc

from conf import API_ROOT
from web.controllers import FeedController
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


@current_app.route('/popular', methods=['GET'])
@etag_match
def popular():
    """
    Return the most popular feeds for the last nb_days days.
    """
    # try to get the 'recent' popular websites, created after
    # 'not_created_before'
    # ie: not_added_before = date_last_added_feed - nb_days
    nb_days = int(request.args.get('nb_days', 1000))
    last_added_feed = FeedController().read().\
                        order_by(desc('created_date')).limit(1)
    if last_added_feed:
        date_last_added_feed = last_added_feed.all()[0].created_date
    else:
        date_last_added_feed = datetime.now()
    not_added_before = date_last_added_feed - timedelta(days=nb_days)

    filters = {}
    filters['created_date__gt'] = not_added_before
    feeds = FeedController().count_by_link(**filters)
    sorted_feeds = sorted(list(feeds.items()), key=operator.itemgetter(1),
                            reverse=True)
    return render_template('popular.html', popular=sorted_feeds)


@current_app.route('/about', methods=['GET'])
@etag_match
def about():
    return render_template('about.html')

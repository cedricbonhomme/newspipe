import logging
import requests.exceptions
from datetime import datetime, timedelta
from sqlalchemy import desc
from werkzeug.exceptions import BadRequest

from flask import Blueprint, render_template, flash, \
                  redirect, request, url_for
from flask_babel import gettext
from flask_login import login_required, current_user

import conf
from web.lib import misc_utils, utils
from web.lib.view_utils import etag_match
from web.lib.feed_utils import construct_feed_from
from web.forms import AddFeedForm
from web.controllers import (CategoryController, FeedController,
                                      ArticleController)

logger = logging.getLogger(__name__)
feeds_bp = Blueprint('feeds', __name__, url_prefix='/feeds')
feed_bp = Blueprint('feed', __name__, url_prefix='/feed')


@feeds_bp.route('/', methods=['GET'])
@login_required
@etag_match
def feeds():
    "Lists the subscribed  feeds in a table."
    art_contr = ArticleController(current_user.id)
    return render_template('feeds.html',
            feeds=FeedController(current_user.id).read().order_by('title'),
            unread_article_count=art_contr.count_by_feed(readed=False),
            article_count=art_contr.count_by_feed())


@feed_bp.route('/<int:feed_id>', methods=['GET'])
@login_required
@etag_match
def feed(feed_id=None):
    "Presents detailed information about a feed."
    feed = FeedController(current_user.id).get(id=feed_id)
    word_size = 6
    category = None
    if feed.category_id:
        category = CategoryController(current_user.id).get(id=feed.category_id)
    articles = ArticleController(current_user.id) \
            .read(feed_id=feed_id) \
            .order_by(desc("date")).all()
    top_words = misc_utils.top_words(articles, n=50, size=int(word_size))
    tag_cloud = misc_utils.tag_cloud(top_words)

    today = datetime.now()
    try:
        last_article = articles[0].date
        first_article = articles[-1].date
        delta = last_article - first_article
        average = round(float(len(articles)) / abs(delta.days), 2)
    except:
        last_article = datetime.fromtimestamp(0)
        first_article = datetime.fromtimestamp(0)
        delta = last_article - first_article
        average = 0
    elapsed = today - last_article

    return render_template('feed.html',
                           head_titles=[utils.clear_string(feed.title)],
                           feed=feed, tag_cloud=tag_cloud,
                           first_post_date=first_article,
                           end_post_date=last_article, category=category,
                           average=average, delta=delta, elapsed=elapsed)


@feed_bp.route('/delete/<feed_id>', methods=['GET'])
@login_required
def delete(feed_id=None):
    feed_contr = FeedController(current_user.id)
    feed = feed_contr.get(id=feed_id)
    feed_contr.delete(feed_id)
    flash(gettext("Feed %(feed_title)s successfully deleted.",
                  feed_title=feed.title), 'success')
    return redirect(url_for('home'))


@feed_bp.route('/reset_errors/<int:feed_id>', methods=['GET', 'POST'])
@login_required
def reset_errors(feed_id):
    feed_contr = FeedController(current_user.id)
    feed = feed_contr.get(id=feed_id)
    feed_contr.update({'id': feed_id}, {'error_count': 0, 'last_error': ''})
    flash(gettext('Feed %(feed_title)r successfully updated.',
                  feed_title=feed.title), 'success')
    return redirect(request.referrer or url_for('home'))


@feed_bp.route('/bookmarklet', methods=['GET', 'POST'])
@login_required
def bookmarklet():
    feed_contr = FeedController(current_user.id)
    url = (request.args if request.method == 'GET' else request.form)\
            .get('url', None)
    if not url:
        flash(gettext("Couldn't add feed: url missing."), "error")
        raise BadRequest("url is missing")

    feed_exists = list(feed_contr.read(__or__={'link': url, 'site_link': url}))
    if feed_exists:
        flash(gettext("Couldn't add feed: feed already exists."),
                "warning")
        return redirect(url_for('feed.form', feed_id=feed_exists[0].id))

    try:
        feed = construct_feed_from(url)
    except requests.exceptions.ConnectionError:
        flash(gettext("Impossible to connect to the address: {}.".format(url)),
              "danger")
        return redirect(url_for('home'))
    except Exception:
        logger.exception('something bad happened when fetching %r', url)
        return redirect(url_for('home'))
    if not feed.get('link'):
        feed['enabled'] = False
        flash(gettext("Couldn't find a feed url, you'll need to find a Atom or"
                      " RSS link manually and reactivate this feed"),
              'warning')
    feed = feed_contr.create(**feed)
    flash(gettext('Feed was successfully created.'), 'success')
    if feed.enabled and conf.CRAWLING_METHOD == "classic":
        misc_utils.fetch(current_user.id, feed.id)
        flash(gettext("Downloading articles for the new feed..."), 'info')
    return redirect(url_for('feed.form', feed_id=feed.id))


@feed_bp.route('/update/<action>/<int:feed_id>', methods=['GET', 'POST'])
@feeds_bp.route('/update/<action>', methods=['GET', 'POST'])
@login_required
def update(action, feed_id=None):
    readed = action == 'read'
    filters = {'readed__ne': readed}

    nb_days = request.args.get('nb_days', 0, type=int)
    if nb_days != 0:
        filters['date__lt'] = datetime.now() - timedelta(days=nb_days)

    if feed_id:
        filters['feed_id'] = feed_id
    ArticleController(current_user.id).update(filters, {'readed': readed})
    flash(gettext('Feed successfully updated.'), 'success')
    return redirect(request.referrer or url_for('home'))


@feed_bp.route('/create', methods=['GET'])
@feed_bp.route('/edit/<int:feed_id>', methods=['GET'])
@login_required
@etag_match
def form(feed_id=None):
    action = gettext("Add a feed")
    categories = CategoryController(current_user.id).read()
    head_titles = [action]
    if feed_id is None:
        form = AddFeedForm()
        form.set_category_choices(categories)
        return render_template('edit_feed.html', action=action,
                               head_titles=head_titles, form=form)
    feed = FeedController(current_user.id).get(id=feed_id)
    form = AddFeedForm(obj=feed)
    form.set_category_choices(categories)
    action = gettext('Edit feed')
    head_titles = [action]
    if feed.title:
        head_titles.append(feed.title)
    return render_template('edit_feed.html', action=action,
                           head_titles=head_titles, categories=categories,
                           form=form, feed=feed)


@feed_bp.route('/create', methods=['POST'])
@feed_bp.route('/edit/<int:feed_id>', methods=['POST'])
@login_required
def process_form(feed_id=None):
    form = AddFeedForm()
    feed_contr = FeedController(current_user.id)
    form.set_category_choices(CategoryController(current_user.id).read())

    if not form.validate():
        return render_template('edit_feed.html', form=form)
    existing_feeds = list(feed_contr.read(link=form.link.data))
    if existing_feeds and feed_id is None:
        flash(gettext("Couldn't add feed: feed already exists."), "warning")
        return redirect(url_for('feed.form', feed_id=existing_feeds[0].id))
    # Edit an existing feed
    feed_attr = {'title': form.title.data, 'enabled': form.enabled.data,
                 'link': form.link.data, 'site_link': form.site_link.data,
                 'filters': [], 'category_id': form.category_id.data}
    if not feed_attr['category_id'] or feed_attr['category_id'] == '0':
        del feed_attr['category_id']

    for filter_attr in ('type', 'pattern', 'action on', 'action'):
        for i, value in enumerate(
                request.form.getlist(filter_attr.replace(' ', '_'))):
            if i >= len(feed_attr['filters']):
                feed_attr['filters'].append({})
            feed_attr['filters'][i][filter_attr] = value

    if feed_id is not None:
        feed_contr.update({'id': feed_id}, feed_attr)
        flash(gettext('Feed %(feed_title)r successfully updated.',
                      feed_title=feed_attr['title']), 'success')
        return redirect(url_for('feed.form', feed_id=feed_id))

    # Create a new feed
    new_feed = feed_contr.create(**feed_attr)

    flash(gettext('Feed %(feed_title)r successfully created.',
                  feed_title=new_feed.title), 'success')

    if conf.CRAWLING_METHOD == "classic":
        misc_utils.fetch(current_user.id, new_feed.id)
        flash(gettext("Downloading articles for the new feed..."), 'info')

    return redirect(url_for('feed.form', feed_id=new_feed.id))


@feeds_bp.route('/inactives', methods=['GET'])
@login_required
def inactives():
    """
    List of inactive feeds.
    """
    nb_days = int(request.args.get('nb_days', 365))
    inactives = FeedController(current_user.id).get_inactives(nb_days)
    return render_template('inactives.html',
                           inactives=inactives, nb_days=nb_days)


@feed_bp.route('/duplicates/<int:feed_id>', methods=['GET'])
@login_required
def duplicates(feed_id):
    """
    Return duplicates article for a feed.
    """
    feed, duplicates = FeedController(current_user.id).get_duplicates(feed_id)
    if len(duplicates) == 0:
        flash(gettext('No duplicates in the feed "{}".').format(feed.title),
                'info')
        return redirect(url_for('home'))
    return render_template('duplicates.html', duplicates=duplicates, feed=feed)

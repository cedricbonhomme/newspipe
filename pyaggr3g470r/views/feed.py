#! /usr/bin/env python
# -*- coding: utf-8 -
import base64
from hashlib import md5
from datetime import datetime
from sqlalchemy import desc
from werkzeug.exceptions import BadRequest

from flask import Blueprint, g, render_template, flash, \
                  redirect, request, url_for, Response
from flask.ext.babel import gettext
from flask.ext.login import login_required

import conf
from pyaggr3g470r import utils
from pyaggr3g470r.lib.feed_utils import construct_feed_from
from pyaggr3g470r.forms import AddFeedForm
from pyaggr3g470r.controllers import FeedController, ArticleController

feeds_bp = Blueprint('feeds', __name__, url_prefix='/feeds')
feed_bp = Blueprint('feed', __name__, url_prefix='/feed')


@feeds_bp.route('/', methods=['GET'])
@login_required
def feeds():
    "Lists the subscribed  feeds in a table."
    art_contr = ArticleController(g.user.id)
    return render_template('feeds.html',
            feeds=FeedController(g.user.id).read(),
            unread_article_count=art_contr.count_by_feed(readed=False),
            article_count=art_contr.count_by_feed())


@feed_bp.route('/<int:feed_id>', methods=['GET'])
@login_required
def feed(feed_id=None):
    "Presents detailed information about a feed."
    feed = FeedController(g.user.id).get(id=feed_id)
    word_size = 6
    articles = ArticleController(g.user.id) \
            .read(feed_id=feed_id) \
            .order_by(desc("Article.date")).all()
    top_words = utils.top_words(articles, n=50, size=int(word_size))
    tag_cloud = utils.tag_cloud(top_words)

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
                           end_post_date=last_article,
                           average=average, delta=delta, elapsed=elapsed)


@feed_bp.route('/delete/<feed_id>', methods=['GET'])
@login_required
def delete(feed_id=None):
    feed_contr = FeedController(g.user.id)
    feed = feed_contr.get(id=feed_id)
    feed_contr.delete(feed_id)
    flash(gettext("Feed %(feed_title)s successfully deleted.",
                  feed_title=feed.title), 'success')
    return redirect(url_for('home'))


@feed_bp.route('/reset_errors/<int:feed_id>', methods=['GET', 'POST'])
@login_required
def reset_errors(feed_id):
    feed_contr = FeedController(g.user.id)
    feed = feed_contr.get(id=feed_id)
    feed_contr.update({'id': feed_id}, {'error_count': 0, 'last_error': ''})
    flash(gettext('Feed %(feed_title)r successfully updated.',
                  feed_title=feed.title), 'success')
    return redirect(request.referrer or url_for('home'))


@feed_bp.route('/bookmarklet', methods=['GET'])
@login_required
def bookmarklet():
    feed_contr = FeedController(g.user.id)
    url = request.args.get('url', None)
    if not url:
        flash(gettext("Couldn't add feed: url missing."), "error")
        raise BadRequest("url is missing")

    feed_exists = list(feed_contr.read(__or__={'link': url, 'site_link': url}))
    if feed_exists:
        flash(gettext("Couldn't add feed: feed already exists."),
                "warning")
        return redirect(url_for('feed.form', feed_id=feed_exists[0].id))

    feed = feed_contr.create(**construct_feed_from(url))
    flash(gettext('Feed was successfully created.'), 'success')
    if conf.CRAWLING_METHOD == "classic":
        utils.fetch(g.user.id, feed.id)
        flash(gettext("Downloading articles for the new feed..."), 'info')
    return redirect(url_for('feed.form', feed_id=feed.id))


@feed_bp.route('/update/<action>/<int:feed_id>', methods=['GET', 'POST'])
@feeds_bp.route('/update/<action>', methods=['GET', 'POST'])
@login_required
def update(action, feed_id=None):
    readed = action == 'read'
    filters = {'readed__ne': readed}
    if feed_id:
        filters['feed_id'] = feed_id
    ArticleController(g.user.id).update(filters, {'readed': readed})
    flash(gettext('Feed successfully updated.'), 'success')
    return redirect(request.referrer or url_for('home'))


@feed_bp.route('/create', methods=['GET'])
@feed_bp.route('/edit/<int:feed_id>', methods=['GET'])
@login_required
def form(feed_id=None):
    action = gettext("Add a feed")
    head_titles = [action]
    if feed_id is None:
        return render_template('edit_feed.html', action=action,
                               head_titles=head_titles, form=AddFeedForm())
    feed = FeedController(g.user.id).get(id=feed_id)
    action = gettext('Edit feed')
    head_titles = [action]
    if feed.title:
        head_titles.append(feed.title)
    return render_template('edit_feed.html', action=action,
                           head_titles=head_titles,
                           form=AddFeedForm(obj=feed), feed=feed)


@feed_bp.route('/create', methods=['POST'])
@feed_bp.route('/edit/<int:feed_id>', methods=['POST'])
@login_required
def process_form(feed_id=None):
    form = AddFeedForm()
    feed_contr = FeedController(g.user.id)

    if not form.validate():
        return render_template('edit_feed.html', form=form)
    existing_feeds = list(feed_contr.read(link=form.link.data))
    if existing_feeds and feed_id is None:
        flash(gettext("Couldn't add feed: feed already exists."), "warning")
        return redirect(url_for('feed.form', feed_id=existing_feeds[0].id))
    # Edit an existing feed
    feed_attr = {'title': form.title.data, 'enabled': form.enabled.data,
                 'link': form.link.data, 'site_link': form.site_link.data,
                 'filters': []}

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
    new_feed = FeedController(g.user.id).create(**feed_attr)

    flash(gettext('Feed %(feed_title)r successfully created.',
                  feed_title=new_feed.title), 'success')

    if conf.CRAWLING_METHOD == "classic":
        utils.fetch(g.user.id, new_feed.id)
        flash(gettext("Downloading articles for the new feed..."), 'info')

    return redirect(url_for('feed.form', feed_id=new_feed.id))


@feed_bp.route('/icon/<int:feed_id>', methods=['GET'])
@login_required
def icon(feed_id):
    icon = FeedController(g.user.id).get(id=feed_id).icon
    etag = md5(icon.encode('utf8')).hexdigest()
    headers = {'Cache-Control': 'max-age=86400', 'ETag': etag}
    if request.headers.get('if-none-match') == etag:
        return Response(status=304, headers=headers)
    return Response(base64.b64decode(icon), mimetype='image', headers=headers)

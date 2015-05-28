#! /usr/bin/env python
# -*- coding: utf-8 -

from datetime import datetime
from sqlalchemy import desc
from werkzeug.exceptions import BadRequest

from flask import Blueprint, g, render_template, flash, \
                  redirect, request, url_for
from flask.ext.babel import gettext
from flask.ext.login import login_required

import conf
from pyaggr3g470r import utils
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
            article_count=art_contr.count_by_feed(),
            )


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

    existing_feeds = list(feed_contr.read(link=url))
    if existing_feeds:
        flash(gettext("Couldn't add feed: feed already exists."),
                "warning")
        return redirect(url_for('feed.form',
                                feed_id=existing_feeds[0].id))

    feed = feed_contr.create(link=url)
    flash(gettext('Feed was successfully created.'), 'success')
    if conf.CRAWLING_METHOD == "classic":
        utils.fetch(g.user.id, feed.id)
        flash(gettext("Downloading articles for the new feed..."), 'info')
    return redirect(url_for('feed.form', feed_id=feed.id))


@feed_bp.route('/read/<int:feed_id>', methods=['GET', 'POST'])
@login_required
def read(feed_id):
    FeedController(g.user.id).update(readed=True)
    flash(gettext('Feed successfully updated.',
                  feed_title=feed.title), 'success')
    return redirect(request.referrer or url_for('home'))


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


@feed_bp.route('/create', methods=['GET', 'POST', 'PUT'])
@feed_bp.route('/edit/<int:feed_id>', methods=['GET', 'POST'])
@login_required
def form(feed_id=None):
    form = AddFeedForm()
    feed_contr = FeedController(g.user.id)

    if request.method == 'POST':
        if not form.validate():
            return render_template('edit_feed.html', form=form)
        existing_feeds = list(feed_contr.read(link=form.link.data))
        if existing_feeds and feed_id is None:
            flash(gettext("Couldn't add feed: feed already exists."),
                  "warning")
            return redirect(url_for('feed.form',
                                    feed_id=existing_feeds[0].id))
        # Edit an existing feed
        if feed_id is not None:
            feed_contr.update({'id': feed_id},
                              {'title': form.title.data,
                               'link': form.link.data,
                               'enabled': form.enabled.data,
                               'site_link': form.site_link.data})
            flash(gettext('Feed %(feed_title)r successfully updated.',
                          feed_title=form.title.data), 'success')
            return redirect(url_for('feed.form', feed_id=feed_id))

        # Create a new feed
        new_feed = FeedController(g.user.id).create(
                        title=form.title.data,
                        description="",
                        link=form.link.data,
                        site_link=form.site_link.data,
                        enabled=form.enabled.data)

        flash(gettext('Feed %(feed_title)r successfully created.',
                      feed_title=new_feed.title), 'success')

        if conf.CRAWLING_METHOD == "classic":
            utils.fetch(g.user.id, new_feed.id)
            flash(gettext("Downloading articles for the new feed..."), 'info')

        return redirect(url_for('feed.form',
                                feed_id=new_feed.id))

    # Getting the form for an existing feed
    if feed_id is not None:
        feed = FeedController(g.user.id).get(id=feed_id)
        form = AddFeedForm(obj=feed)
        return render_template('edit_feed.html',
                               action=gettext("Edit the feed"),
                               form=form, feed=feed)

    # Return an empty form in order to create a new feed
    return render_template('edit_feed.html', action=gettext("Add a feed"),
                           form=form)

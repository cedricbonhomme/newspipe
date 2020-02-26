import pytz
import logging
from datetime import datetime

from flask import current_app, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
from flask_babel import gettext, get_locale
from babel.dates import format_datetime, format_timedelta

import conf
from lib.utils import redirect_url
from lib import misc_utils
from web.lib.view_utils import etag_match
from web.views.common import jsonify

from web.controllers import FeedController, ArticleController, CategoryController

localize = pytz.utc.localize
logger = logging.getLogger(__name__)


@current_app.route("/")
@login_required
def home():

    art_contr = ArticleController(current_user.id)

    unread = art_contr.count_by_feed(readed=False)

    feeds = {feed.id: feed.title for feed in current_user.feeds}
    # articles = Article.query.filter(Article.feed_id.in_(feeds.keys()),
    #                                 Article.user_id == current_user.id)
    filter_ = request.args.get('filter_', 'unread')
    feed_id = int(request.args.get('feed', 0))
    limit = request.args.get('limit', 1000)

    if filter_ != 'all':
        articles = art_contr.read_light(readed=(filter_ == 'read'))
    if feed_id:
        articles = art_contr.read_light(readed=(filter_ == 'read'), feed_id=feed_id)

    # articles = articles.order_by(Article.date.desc())
    if limit != 'all':
        limit = int(limit)
        articles = articles.limit(limit)

    # unread = db.session.query(Article.feed_id, func.count(Article.id))\
    #                    .filter(Article.readed == False, Article.user_id == g.user.id)\
    #                    .group_by(Article.feed_id).all()


    in_error = {feed.id: feed.error_count for feed in
                FeedController(current_user.id).read(error_count__gt=0).all()}
    def gen_url(filter_=filter_, limit=limit, feed=feed_id):
        return '?filter_=%s&limit=%s&feed=%d' % (filter_, limit, feed)
    return render_template('home.html', gen_url=gen_url, feed_id=feed_id,
                           filter_=filter_, limit=limit, feeds=feeds,
                           unread=dict(unread), articles=articles.all(),
                           in_error=in_error)


@current_app.route("/menu")
@login_required
@etag_match
@jsonify
def get_menu():
    now, locale = datetime.now(), get_locale()
    categories_order = [0]
    categories = {0: {"name": "No category", "id": 0}}
    for cat in CategoryController(current_user.id).read().order_by("name"):
        categories_order.append(cat.id)
        categories[cat.id] = cat
    unread = ArticleController(current_user.id).count_by_feed(readed=False)
    for cat_id in categories:
        categories[cat_id]["unread"] = 0
        categories[cat_id]["feeds"] = []
    feeds = {feed.id: feed for feed in FeedController(current_user.id).read()}
    for feed_id, feed in feeds.items():
        feed["created_rel"] = format_timedelta(
            feed.created_date - now, add_direction=True, locale=locale
        )
        feed["last_rel"] = format_timedelta(
            feed.last_retrieved - now, add_direction=True, locale=locale
        )
        feed["created_date"] = format_datetime(
            localize(feed.created_date), locale=locale
        )
        feed["last_retrieved"] = format_datetime(
            localize(feed.last_retrieved), locale=locale
        )
        feed["category_id"] = feed.category_id or 0
        feed["unread"] = unread.get(feed.id, 0)
        if not feed.filters:
            feed["filters"] = []
        if feed.icon_url:
            feed["icon_url"] = url_for("icon.icon", url=feed.icon_url)
        categories[feed["category_id"]]["unread"] += feed["unread"]
        categories[feed["category_id"]]["feeds"].append(feed_id)
    return {
        "feeds": feeds,
        "categories": categories,
        "categories_order": categories_order,
        "crawling_method": conf.CRAWLING_METHOD,
        "max_error": conf.DEFAULT_MAX_ERROR,
        "error_threshold": conf.ERROR_THRESHOLD,
        "is_admin": current_user.is_admin,
        "all_unread_count": sum(unread.values()),
    }


def _get_filters(in_dict):
    filters = {}
    query = in_dict.get("query")
    if query:
        search_title = in_dict.get("search_title") == "true"
        search_content = in_dict.get("search_content") == "true"
        if search_title:
            filters["title__ilike"] = "%%%s%%" % query
        if search_content:
            filters["content__ilike"] = "%%%s%%" % query
        if len(filters) == 0:
            filters["title__ilike"] = "%%%s%%" % query
        if len(filters) > 1:
            filters = {"__or__": filters}
    if in_dict.get("filter") == "unread":
        filters["readed"] = False
    elif in_dict.get("filter") == "liked":
        filters["like"] = True
    filter_type = in_dict.get("filter_type")
    if filter_type in {"feed_id", "category_id"} and in_dict.get("filter_id"):
        filters[filter_type] = int(in_dict["filter_id"]) or None
    return filters


@jsonify
def _articles_to_json(articles, fd_hash=None):
    now, locale = datetime.now(), get_locale()
    fd_hash = {
        feed.id: {
            "title": feed.title,
            "icon_url": url_for("icon.icon", url=feed.icon_url)
            if feed.icon_url
            else None,
        }
        for feed in FeedController(current_user.id).read()
    }

    return {
        "articles": [
            {
                "title": art.title,
                "liked": art.like,
                "read": art.readed,
                "article_id": art.id,
                "selected": False,
                "feed_id": art.feed_id,
                "category_id": art.category_id or 0,
                "feed_title": fd_hash[art.feed_id]["title"] if fd_hash else None,
                "icon_url": fd_hash[art.feed_id]["icon_url"] if fd_hash else None,
                "date": format_datetime(localize(art.date), locale=locale),
                "rel_date": format_timedelta(
                    art.date - now, threshold=1.1, add_direction=True, locale=locale
                ),
            }
            for art in articles.limit(1000)
        ]
    }


@current_app.route("/getart/<int:article_id>")
@current_app.route("/getart/<int:article_id>/<parse>")
@login_required
@etag_match
@jsonify
def get_article(article_id, parse=False):
    locale = get_locale()
    contr = ArticleController(current_user.id)
    article = contr.get(id=article_id)
    if not article.readed:
        article["readed"] = True
        contr.update({"id": article_id}, {"readed": True})
    article["category_id"] = article.category_id or 0
    feed = FeedController(current_user.id).get(id=article.feed_id)
    article["icon_url"] = (
        url_for("icon.icon", url=feed.icon_url) if feed.icon_url else None
    )
    article["date"] = format_datetime(localize(article.date), locale=locale)
    return article


@current_app.route("/mark_all_as_read", methods=["PUT"])
@login_required
def mark_all_as_read():
    filters = _get_filters(request.json)
    acontr = ArticleController(current_user.id)
    processed_articles = _articles_to_json(acontr.read_light(**filters))
    acontr.update(filters, {"readed": True})
    return processed_articles


@current_app.route("/fetch", methods=["GET"])
@current_app.route("/fetch/<int:feed_id>", methods=["GET"])
@login_required
def fetch(feed_id=None):
    """
    Triggers the download of news.
    News are downloaded in a separated process.
    """
    if conf.CRAWLING_METHOD == "default" and current_user.is_admin:
        misc_utils.fetch(current_user.id, feed_id)
        flash(gettext("Downloading articles..."), "info")
    else:
        flash(
            gettext(
                "The manual retrieving of news is only available "
                + "for administrator, on the Heroku platform."
            ),
            "info",
        )
    return redirect(redirect_url())

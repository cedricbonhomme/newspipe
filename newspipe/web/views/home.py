import pytz
import logging
from datetime import datetime

from flask import current_app, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
from flask_babel import gettext, get_locale
from babel.dates import format_datetime, format_timedelta

from newspipe.bootstrap import application
from newspipe.lib.utils import redirect_url
from newspipe.lib import misc_utils
from newspipe.web.lib.view_utils import etag_match
from newspipe.web.views.common import jsonify

from newspipe.controllers import FeedController, ArticleController, CategoryController

localize = pytz.utc.localize
logger = logging.getLogger(__name__)


@current_app.route("/")
@login_required
def home():
    """Displays the home page of the connected user.
    """
    art_contr = ArticleController(current_user.id)

    unread = art_contr.count_by_feed(readed=False)
    nb_unread = art_contr.read_light(readed=False).count()

    feeds = {
        feed.id: feed
        for feed in sorted(
            current_user.feeds, key=lambda x: x.title.lower(), reverse=False
        )
    }

    filter_ = request.args.get("filter_", "unread")
    feed_id = int(request.args.get("feed", 0))
    liked = int(request.args.get("liked", 0)) == 1
    limit = request.args.get("limit", 1000)

    filters = {}
    if filter_ in ["read", "unread"]:
        filters["readed"] = filter_ == "read"
    if feed_id:
        filters["feed_id"] = feed_id
    if liked:
        filters["like"] = int(liked) == 1

    articles = art_contr.read_ordered(**filters)

    if limit != "all":
        limit = int(limit)
        articles = articles.limit(limit)

    in_error = {
        feed.id: feed.error_count
        for feed in FeedController(current_user.id).read(error_count__gt=0).all()
    }

    def gen_url(filter_=filter_, limit=limit, feed=feed_id, liked=liked):
        return "?filter_=%s&limit=%s&feed=%d&liked=%s" % (
            filter_,
            limit,
            feed,
            1 if liked else 0,
        )

    return render_template(
        "home.html",
        nb_unread=nb_unread,
        gen_url=gen_url,
        feed_id=feed_id,
        filter_=filter_,
        limit=limit,
        feeds=feeds,
        liked=liked,
        unread=dict(unread),
        articles=articles.all(),
        in_error=in_error,
    )


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
    if application.config["CRAWLING_METHOD"] == "default" and current_user.is_admin:
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

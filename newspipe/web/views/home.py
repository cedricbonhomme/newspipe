import logging
from datetime import datetime

import pytz
from babel.dates import format_datetime
from babel.dates import format_timedelta
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_babel import get_locale
from flask_babel import gettext
from flask_login import current_user
from flask_login import login_required

from newspipe.bootstrap import application
from newspipe.controllers import ArticleController
from newspipe.controllers import CategoryController
from newspipe.controllers import FeedController
from newspipe.lib import misc_utils
from newspipe.lib.utils import safe_redirect_url
from newspipe.web.lib.view_utils import etag_match
from newspipe.web.views.common import jsonify

localize = pytz.utc.localize
logger = logging.getLogger(__name__)


@current_app.route("/")
@login_required
def home():
    """Displays the home page of the connected user."""
    filters = _get_filters(request.args)

    category_contr = CategoryController(current_user.id)
    art_contr = ArticleController(current_user.id)
    categories = {cat.id: cat for cat in category_contr.read().all()}

    unread = art_contr.count_by_feed(readed=False)
    nb_unread = art_contr.read_light(readed=False).count()

    unread_by_cat = art_contr.count_by_category(readed=False)

    feeds = {
        feed.id: feed
        for feed in sorted(
            current_user.feeds, key=lambda x: x.title.lower(), reverse=False
        )
    }

    filter_ = request.args.get("filter_", "unread")
    feed_id = int(request.args.get("feed", 0))
    category_id = int(request.args.get("category", 0))
    liked = int(request.args.get("liked", 0)) == 1
    limit = request.args.get("limit", 1000)
    query = request.args.get("query", "")
    search_title = request.args.get("search_title", "off")
    search_content = request.args.get("search_content", "off")

    if filter_ in ["read", "unread"]:
        filters["readed"] = filter_ == "read"
    if feed_id:
        filters["feed_id"] = feed_id
    if category_id:
        filters["category_id"] = category_id
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

    def gen_url(
        filter_=filter_,
        limit=limit,
        feed=feed_id,
        category=category_id,
        liked=liked,
        query=query,
        search_title=search_title,
        search_content=search_content,
    ):
        return (
            "?filter_=%s&limit=%s&feed=%d&category=%d&liked=%s&query=%s&search_title=%s&search_content=%s"
            % (
                filter_,
                limit,
                feed,
                category,
                1 if liked else 0,
                query,
                search_title,
                search_content,
            )
        )

    return render_template(
        "home.html",
        nb_unread=nb_unread,
        gen_url=gen_url,
        feed_id=feed_id,
        category_id=category_id,
        filter_=filter_,
        limit=limit,
        feeds=feeds,
        categories=categories,
        unread_by_cat=unread_by_cat,
        liked=liked,
        unread=dict(unread),
        articles=articles.all(),
        in_error=in_error,
    )


def _get_filters(in_dict):
    filters = {}
    query = in_dict.get("query")
    if query:
        search_title = in_dict.get("search_title") == "on"
        search_content = in_dict.get("search_content") == "on"
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
            "icon_url": (
                url_for("icon.icon", url=feed.icon_url) if feed.icon_url else None
            ),
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
        flash(gettext("Fetching articles…"), "info")
    else:
        flash(
            gettext(
                "The manual retrieving of news is only available "
                "for administrator, on the Heroku platform."
            ),
            "info",
        )
    url = safe_redirect_url()
    if url:
        return redirect(url)
    else:
        return "Error"

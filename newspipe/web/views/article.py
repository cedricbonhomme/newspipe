from datetime import datetime, timedelta

from flask import (
    Blueprint,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_babel import gettext
from flask_login import current_user, login_required

from newspipe.bootstrap import db
from newspipe.controllers import ArticleController, UserController
from newspipe.lib.data import export_json
from newspipe.lib.utils import clear_string, safe_redirect_url
from newspipe.web.lib.view_utils import etag_match

articles_bp = Blueprint("articles", __name__, url_prefix="/articles")
article_bp = Blueprint("article", __name__, url_prefix="/article")


@article_bp.route("/redirect/<int:article_id>", methods=["GET"])
@login_required
def redirect_to_article(article_id):
    contr = ArticleController(current_user.id)
    article = contr.get(id=article_id)
    if not article.readed:
        contr.update({"id": article.id}, {"readed": True})
    return redirect(article.link)


@article_bp.route("/<int:article_id>", methods=["GET"])
@login_required
@etag_match
def article(article_id=None):
    """
    Presents an article.
    """
    art_contr = ArticleController(current_user.id)
    article = art_contr.get(id=article_id)
    if not article.readed:
        art_contr.update({"id": article.id}, {"readed": True})
    return render_template(
        "article.html", head_titles=[clear_string(article.title)], article=article
    )


@article_bp.route("/public/<int:article_id>", methods=["GET"])
@etag_match
def article_pub(article_id=None):
    """
    Presents an article of a public feed if the profile of the owner is also
    public.
    """
    article = ArticleController().get(id=article_id)
    if article.source.private or not article.source.user.is_public_profile:
        return render_template("errors/404.html"), 404
    return render_template(
        "article_pub.html", head_titles=[clear_string(article.title)], article=article
    )


@article_bp.route("/delete/<int:article_id>", methods=["GET"])
@login_required
def delete(article_id=None):
    """
    Delete an article from the database.
    """
    article = ArticleController(current_user.id).delete(article_id)
    flash(
        gettext("Article %(article_title)s deleted", article_title=article.title),
        "success",
    )
    return redirect(url_for("home"))


@articles_bp.route("/history", methods=["GET"])
@articles_bp.route("/history/<int:year>", methods=["GET"])
@articles_bp.route("/history/<int:year>/<int:month>", methods=["GET"])
@login_required
def history(year=None, month=None):
    if month is not None:
        cntr, articles = ArticleController(current_user.id).get_history(year, month)
    else:
        cntr, articles = {}, []
    return render_template(
        "history.html", articles_counter=cntr, articles=articles, year=year, month=month
    )


@article_bp.route("/mark_as/<string:new_value>", methods=["GET"])
@article_bp.route("/mark_as/<string:new_value>/feed/<int:feed_id>", methods=["GET"])
@login_required
def mark_as(new_value="read", feed_id=None, article_id=None):
    """
    Mark a single article or all articles of a feed as read/unread.
    """
    readed = new_value == "read"
    art_contr = ArticleController(current_user.id)
    filters = {"readed": not readed}
    if feed_id is not None:
        filters["feed_id"] = feed_id
        message = "Feed marked as %s."
    elif article_id is not None:
        filters["id"] = article_id
        message = "Article marked as %s."
    else:
        message = "All article marked as %s."
    art_contr.update(filters, {"readed": readed})
    flash(gettext(message % new_value), "info")

    # if readed:
    #     return redirect(safe_redirect_url())
    return redirect(url_for("home"))


@articles_bp.route("/expire_articles", methods=["GET"])
@login_required
def expire():
    """
    Delete articles older than the given number of weeks.
    """
    current_time = datetime.utcnow()
    weeks_ago = current_time - timedelta(int(request.args.get("weeks", 10)))
    art_contr = ArticleController(current_user.id)

    query = art_contr.read(
        __or__={"date__lt": weeks_ago, "retrieved_date__lt": weeks_ago}
    )
    count = query.count()
    query.delete()
    db.session.commit()
    flash(gettext("%(count)d articles deleted", count=count), "info")
    url = safe_redirect_url()
    if url:
        return redirect(url)
    else:
        return "Error"


@articles_bp.route("/export", methods=["GET"])
@login_required
def export():
    """
    Export articles to JSON.
    """
    user = UserController(current_user.id).get(id=current_user.id)
    json_result = {}
    try:
        json_result = export_json(user)
    except Exception:
        flash(gettext("Error when exporting articles."), "danger")
        url = safe_redirect_url()
        if url:
            return redirect(url)
        else:
            return "Error"
    response = make_response(json_result)
    response.mimetype = "application/json"
    response.headers["Content-Disposition"] = "attachment; filename=account.json"
    return response

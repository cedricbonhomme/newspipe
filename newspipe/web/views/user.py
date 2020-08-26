from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_babel import gettext
from flask_login import current_user, login_required
from flask_paginate import Pagination, get_page_args

from newspipe.bootstrap import application
from newspipe.controllers import (
    ArticleController,
    BookmarkController,
    CategoryController,
    FeedController,
    UserController,
)
from newspipe.lib import misc_utils
from newspipe.lib.data import import_json, import_opml
from newspipe.web.forms import ProfileForm
from newspipe.web.lib.user_utils import confirm_token

users_bp = Blueprint("users", __name__, url_prefix="/users")
user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/<string:nickname>", methods=["GET"])
def profile_public(nickname=None):
    """
    Display the public profile of the user.
    """
    category_id = int(request.args.get("category_id", 0))
    user_contr = UserController()
    user = user_contr.get(nickname=nickname)
    if not user.is_public_profile:
        if current_user.is_authenticated and current_user.id == user.id:
            flash(gettext("You must set your profile to public."), "info")
        return redirect(url_for("user.profile"))

    filters = {}
    filters["private"] = False
    if category_id:
        filters["category_id"] = category_id
    feeds = FeedController(user.id).read(**filters)

    return render_template(
        "profile_public.html", user=user, feeds=feeds, selected_category_id=category_id
    )


@user_bp.route(
    "/<string:nickname>/stream", defaults={"per_page": "25"}, methods=["GET"]
)
def user_stream(per_page, nickname=None):
    """
    Display the stream of a user (list of articles of public feed).
    """
    user_contr = UserController()
    user = user_contr.get(nickname=nickname)
    if not user.is_public_profile:
        if current_user.is_authenticated and current_user.id == user.id:
            flash(gettext("You must set your profile to public."), "info")
        return redirect(url_for("user.profile"))

    category_id = int(request.args.get("category_id", 0))
    category = CategoryController().read(id=category_id).first()

    # Load the public feeds
    filters = {}
    filters["private"] = False
    if category_id:
        filters["category_id"] = category_id
    feeds = FeedController().read(**filters).all()

    # Re-initializes the filters to load the articles
    filters = {}
    filters["feed_id__in"] = [feed.id for feed in feeds]
    if category:
        filters["category_id"] = category_id
    articles = ArticleController(user.id).read(**filters)

    # Server-side pagination
    page, per_page, offset = get_page_args(per_page_parameter="per_page")
    pagination = Pagination(
        page=page,
        total=articles.count(),
        css_framework="bootstrap4",
        search=False,
        record_name="articles",
        per_page=per_page,
    )

    return render_template(
        "user_stream.html",
        user=user,
        articles=articles.offset(offset).limit(per_page),
        category=category,
        pagination=pagination,
    )


@user_bp.route("/management", methods=["GET", "POST"])
@login_required
def management():
    """
    Display the management page.
    """
    if request.method == "POST":
        if None != request.files.get("opmlfile", None):
            # Import an OPML file
            data = request.files.get("opmlfile", None)
            if not misc_utils.allowed_file(data.filename):
                flash(gettext("File not allowed."), "danger")
            else:
                try:
                    nb = import_opml(current_user.nickname, data.read())
                    if application.config["CRAWLING_METHOD"] == "classic":
                        misc_utils.fetch(current_user.id, None)
                        flash(str(nb) + "  " + gettext("feeds imported."), "success")
                        flash(gettext("Downloading articles..."), "info")
                except:
                    flash(gettext("Impossible to import the new feeds."), "danger")
        elif None != request.files.get("jsonfile", None):
            # Import an account
            data = request.files.get("jsonfile", None)
            if not misc_utils.allowed_file(data.filename):
                flash(gettext("File not allowed."), "danger")
            else:
                try:
                    nb = import_json(current_user.nickname, data.read())
                    flash(gettext("Account imported."), "success")
                except:
                    flash(gettext("Impossible to import the account."), "danger")
        else:
            flash(gettext("File not allowed."), "danger")

    nb_feeds = FeedController(current_user.id).read().count()
    art_contr = ArticleController(current_user.id)
    nb_articles = art_contr.read().count()
    nb_unread_articles = art_contr.read(readed=False).count()
    nb_categories = CategoryController(current_user.id).read().count()
    nb_bookmarks = BookmarkController(current_user.id).read().count()
    return render_template(
        "management.html",
        user=current_user,
        nb_feeds=nb_feeds,
        nb_articles=nb_articles,
        nb_unread_articles=nb_unread_articles,
        nb_categories=nb_categories,
        nb_bookmarks=nb_bookmarks,
    )


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """
    Edit the profile of the currently logged user.
    """
    user_contr = UserController(current_user.id)
    user = user_contr.get(id=current_user.id)
    form = ProfileForm()

    if request.method == "POST":
        if form.validate():
            try:
                user_contr.update(
                    {"id": current_user.id},
                    {
                        "nickname": form.nickname.data,
                        "password": form.password.data,
                        "automatic_crawling": form.automatic_crawling.data,
                        "is_public_profile": form.is_public_profile.data,
                        "bio": form.bio.data,
                        "webpage": form.webpage.data,
                        "twitter": form.twitter.data,
                    },
                )
            except Exception as error:
                flash(
                    gettext(
                        "Problem while updating your profile: " "%(error)s", error=error
                    ),
                    "danger",
                )
            else:
                flash(
                    gettext("User %(nick)s successfully updated", nick=user.nickname),
                    "success",
                )
            return redirect(url_for("user.profile"))
        else:
            return render_template("profile.html", user=user, form=form)

    if request.method == "GET":
        form = ProfileForm(obj=user)
        return render_template("profile.html", user=user, form=form)


@user_bp.route("/delete_account", methods=["GET"])
@login_required
def delete_account():
    """
    Delete the account of the user (with all its data).
    """
    UserController(current_user.id).delete(current_user.id)
    flash(gettext("Your account has been deleted."), "success")
    return redirect(url_for("logout"))


@user_bp.route("/confirm_account/<string:token>", methods=["GET"])
def confirm_account(token=None):
    """
    Confirm the account of a user.
    """
    user_contr = UserController()
    user, nickname = None, None
    if token != "":
        nickname = confirm_token(token)
    if nickname:
        user = user_contr.read(nickname=nickname).first()
    if user is not None:
        user_contr.update({"id": user.id}, {"is_active": True})
        flash(gettext("Your account has been confirmed."), "success")
    else:
        flash(gettext("Impossible to confirm this account."), "danger")
    return redirect(url_for("login"))

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_babel import gettext
from flask_login import current_user
from flask_login import login_required
from flask_paginate import get_page_args
from flask_paginate import Pagination

from newspipe.bootstrap import application
from newspipe.controllers import ArticleController
from newspipe.controllers import ArticleNoteController
from newspipe.controllers import BookmarkController
from newspipe.controllers import CategoryController
from newspipe.controllers import FeedController
from newspipe.controllers import UserController
from newspipe.lib import misc_utils
from newspipe.lib import twofactor
from newspipe.lib.data import import_json
from newspipe.lib.data import import_opml
from newspipe.web.forms import ProfileForm
from newspipe.web.lib.user_utils import confirm_token

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
    articles = ArticleController(user.id).read_ordered(**filters)

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
        if None is not request.files.get("opmlfile", None):
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
                        flash(gettext("Fetching articles…"), "info")
                except Exception:
                    flash(gettext("Impossible to import the new feeds."), "danger")
        elif None is not request.files.get("jsonfile", None):
            # Import an account
            data = request.files.get("jsonfile", None)
            if not misc_utils.allowed_file(data.filename):
                flash(gettext("File not allowed."), "danger")
            else:
                try:
                    nb = import_json(current_user.nickname, data.read())
                    flash(gettext("Account imported."), "success")
                except Exception:
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


@user_bp.route("/notes", methods=["GET"])
@login_required
def notes():
    """
    Display all the notes written by the current user, newest first.
    """
    query = ArticleNoteController(current_user.id).read_ordered_desc()

    page, per_page, offset = get_page_args()
    pagination = Pagination(
        page=page,
        total=query.count(),
        css_framework="bootstrap5",
        search=False,
        record_name="notes",
        per_page=per_page,
    )

    return render_template(
        "notes.html",
        notes=query.offset(offset).limit(per_page).all(),
        pagination=pagination,
    )


@user_bp.route("/notes/<int:note_id>/delete", methods=["POST"])
@login_required
def delete_note(note_id):
    """
    Delete one of the current user's notes from the "My notes" page.
    """
    ArticleNoteController(current_user.id).delete(note_id)
    flash(gettext("Note deleted."), "success")
    return redirect(url_for("user.notes"))


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
                # for external user, just force the exact same username.
                if user.external_auth or not form.nickname.data:
                    form.nickname.data = user.nickname
                user_contr.update(
                    {"id": current_user.id},
                    {
                        "nickname": form.nickname.data,
                        "password": form.password.data,
                        "automatic_crawling": form.automatic_crawling.data,
                        "is_public_profile": form.is_public_profile.data,
                        "bio": form.bio.data,
                        "webpage": form.webpage.data,
                        "mastodon": form.mastodon.data,
                        "github": form.github.data,
                        "linkedin": form.linkedin.data,
                    },
                )
            except Exception as error:
                flash(
                    gettext(
                        "Problem while updating your profile: %(error)s", error=error
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
        return render_template(
            "profile.html", user=user, form=form, nick_disabled=bool(user.external_auth)
        )


def _render_two_factor(user, new_codes=None):
    qrcode_svg = None
    if user.totp_secret and not user.totp_enabled:
        qrcode_svg = twofactor.qrcode_svg(user)
    return render_template(
        "two_factor.html",
        user=user,
        qrcode_svg=qrcode_svg,
        new_codes=new_codes,
        nb_recovery_codes=twofactor.remaining_recovery_codes(user),
    )


@user_bp.route("/two_factor", methods=["GET"])
@login_required
def two_factor():
    """
    Display the two-factor authentication management page.
    """
    user = UserController(current_user.id).get(id=current_user.id)
    return _render_two_factor(user)


@user_bp.route("/two_factor/enable", methods=["POST"])
@login_required
def two_factor_enable():
    """
    Start the enrollment: generate a secret, to be confirmed with a code.
    """
    user_contr = UserController(current_user.id)
    user = user_contr.get(id=current_user.id)
    if user.totp_enabled:
        flash(gettext("Two-factor authentication is already enabled."), "warning")
    else:
        user_contr.update(
            {"id": user.id},
            {"totp_secret": twofactor.generate_totp_secret(), "totp_enabled": False},
        )
    return redirect(url_for("user.two_factor"))


@user_bp.route("/two_factor/confirm", methods=["POST"])
@login_required
def two_factor_confirm():
    """
    Complete the enrollment by verifying a first TOTP code, then display
    the recovery codes (only once).
    """
    user_contr = UserController(current_user.id)
    user = user_contr.get(id=current_user.id)
    if user.totp_enabled or not user.totp_secret:
        return redirect(url_for("user.two_factor"))

    counter = twofactor.verify_totp(user, request.form.get("code", ""))
    if counter is None:
        flash(gettext("Invalid code."), "danger")
        return redirect(url_for("user.two_factor"))

    codes, hashes = twofactor.generate_recovery_codes()
    user_contr.update(
        {"id": user.id},
        {"totp_enabled": True, "last_totp": counter, "recovery_codes": hashes},
    )
    flash(gettext("Two-factor authentication is now enabled."), "success")
    return _render_two_factor(user, new_codes=codes)


@user_bp.route("/two_factor/cancel", methods=["POST"])
@login_required
def two_factor_cancel():
    """
    Abort a pending (unconfirmed) enrollment.
    """
    user_contr = UserController(current_user.id)
    user = user_contr.get(id=current_user.id)
    if not user.totp_enabled:
        user_contr.update({"id": user.id}, {"totp_secret": None})
    return redirect(url_for("user.two_factor"))


@user_bp.route("/two_factor/disable", methods=["POST"])
@login_required
def two_factor_disable():
    """
    Disable two-factor authentication; requires a valid TOTP or recovery code.
    """
    user_contr = UserController(current_user.id)
    user = user_contr.get(id=current_user.id)
    if not user.totp_enabled:
        return redirect(url_for("user.two_factor"))

    code = request.form.get("code", "")
    if (
        twofactor.verify_totp(user, code) is None
        and twofactor.consume_recovery_code(user, code) is None
    ):
        flash(gettext("Invalid code."), "danger")
        return redirect(url_for("user.two_factor"))

    user_contr.update(
        {"id": user.id},
        {
            "totp_secret": None,
            "totp_enabled": False,
            "last_totp": None,
            "recovery_codes": None,
        },
    )
    flash(gettext("Two-factor authentication has been disabled."), "success")
    return redirect(url_for("user.two_factor"))


@user_bp.route("/two_factor/recovery", methods=["POST"])
@login_required
def two_factor_recovery():
    """
    Regenerate the recovery codes; requires a valid TOTP code.
    """
    user_contr = UserController(current_user.id)
    user = user_contr.get(id=current_user.id)
    if not user.totp_enabled:
        return redirect(url_for("user.two_factor"))

    counter = twofactor.verify_totp(user, request.form.get("code", ""))
    if counter is None:
        flash(gettext("Invalid code."), "danger")
        return redirect(url_for("user.two_factor"))

    codes, hashes = twofactor.generate_recovery_codes()
    user_contr.update({"id": user.id}, {"last_totp": counter, "recovery_codes": hashes})
    flash(
        gettext("New recovery codes generated. The old ones are no longer valid."),
        "success",
    )
    return _render_two_factor(user, new_codes=codes)


@user_bp.route("/delete_account", methods=["POST"])
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

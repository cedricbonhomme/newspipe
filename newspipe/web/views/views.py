import logging
import operator
import sys
from datetime import datetime
from datetime import timedelta

from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_babel import gettext
from sqlalchemy import desc

from newspipe.bootstrap import application
from newspipe.bootstrap import talisman
from newspipe.controllers import FeedController
from newspipe.controllers import UserController
from newspipe.web import __version__
from newspipe.web.lib.view_utils import etag_match

logger = logging.getLogger(__name__)


@current_app.errorhandler(401)
def authentication_required(error):
    if application.conf["API_ROOT"] in request.url:
        return error
    flash(gettext("Authentication required."), "info")
    return redirect(url_for("login"))


@current_app.errorhandler(403)
def authentication_failed(error):
    if application.conf["API_ROOT"] in request.url:
        return error
    flash(gettext("Forbidden."), "danger")
    return redirect(url_for("login"))


@current_app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@current_app.errorhandler(500)
def internal_server_error(error):
    return render_template("errors/500.html"), 500


@current_app.errorhandler(AssertionError)
def handle_sqlalchemy_assertion_error(error):
    return error.args[0], 400


@current_app.route("/popular", methods=["GET"])
@etag_match
def popular():
    """
    Return the most popular feeds for the last nb_days days.
    """
    # try to get the 'recent' popular websites, created after
    # 'not_created_before'
    # ie: not_added_before = date_last_added_feed - nb_days
    try:
        nb_days = int(request.args.get("nb_days", 365))
    except ValueError:
        nb_days = 10000
    last_added_feed = (
        FeedController().read().order_by(desc("created_date")).limit(1).all()
    )
    if last_added_feed:
        date_last_added_feed = last_added_feed[0].created_date
    else:
        date_last_added_feed = datetime.now()
    not_added_before = date_last_added_feed - timedelta(days=nb_days)

    filters = {}
    filters["created_date__gt"] = not_added_before
    filters["private"] = False
    filters["error_count__lt"] = application.config["DEFAULT_MAX_ERROR"]
    feeds = FeedController().count_by_link(**filters)
    sorted_feeds = sorted(list(feeds.items()), key=operator.itemgetter(1), reverse=True)
    return render_template("popular.html", popular=sorted_feeds)


@current_app.route("/about", methods=["GET"])
@etag_match
def about():
    return render_template("about.html", contact=application.config["ADMIN_EMAIL"])


@current_app.route("/about/more", methods=["GET"])
@etag_match
def about_more():
    version = __version__.split("-")
    if len(version) == 1:
        newspipe_version = version[0]
        version_url = f"https://git.sr.ht/~cedric/newspipe/refs/{version[0]}"
    else:
        newspipe_version = f"{version[0]} - {version[2][1:]}"
        version_url = "https://git.sr.ht/~cedric/newspipe/commit/{}".format(
            version[2][1:]
        )

    talisman._parse_policy(talisman.content_security_policy)

    return render_template(
        "about_more.html",
        newspipe_version=newspipe_version,
        version_url=version_url,
        registration=[application.config["SELF_REGISTRATION"] and "Open" or "Closed"][
            0
        ],
        python_version="{}.{}.{}".format(*sys.version_info[:3]),
        nb_users=UserController().read().count(),
        content_security_policy=talisman._parse_policy(
            talisman.content_security_policy
        ),
    )


@current_app.route("/robots.txt", methods=["GET"])
def robots():
    """Robots dot txt page."""
    return render_template("robots.txt"), 200, {"Content-Type": "text/plain"}

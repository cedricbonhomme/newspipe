import json
import logging
from datetime import datetime
from datetime import timezone

from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_babel import gettext
from flask_login import current_user
from flask_login import login_required
from flask_login import LoginManager
from flask_login import logout_user
from flask_principal import AnonymousIdentity
from flask_principal import identity_changed
from flask_principal import identity_loaded
from flask_principal import Principal
from flask_principal import session_identity_loader
from flask_principal import UserNeed
from werkzeug.exceptions import NotFound
from werkzeug.security import generate_password_hash

from newspipe.bootstrap import application
from newspipe.controllers import UserController
from newspipe.lib import twofactor
from newspipe.notifications import notifications
from newspipe.web.forms import SigninForm
from newspipe.web.forms import SignupForm
from newspipe.web.forms import TwoFactorForm
from newspipe.web.views.common import admin_role
from newspipe.web.views.common import api_role
from newspipe.web.views.common import login_user_bundle

Principal(current_app)
# Create a permission with a single Need, in this case a RoleNeed.

login_manager = LoginManager()
login_manager.init_app(current_app)
login_manager.login_view = "login"
login_manager.login_message = ""
# login_manager.login_message_category = "info"

logger = logging.getLogger(__name__)


@identity_loaded.connect_via(current_app._get_current_object())  # type: ignore
def on_identity_loaded(sender, identity) -> None:
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if current_user.is_authenticated:
        identity.provides.add(UserNeed(current_user.id))
        if current_user.is_admin:
            identity.provides.add(admin_role)
        if current_user.is_api:
            identity.provides.add(api_role)


@login_manager.user_loader
def load_user(user_id):
    try:
        return UserController(user_id, ignore_context=True).get(
            id=user_id, is_active=True
        )
    except NotFound:
        pass


@current_app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = SigninForm()

    if (
        request.method == "POST" and form.validate() and form.user is not None
    ):  # fixes an issue in flask-wtf
        if form.user.totp_enabled:
            # password OK but a second factor is required: defer the login
            session["twofactor_user_id"] = form.user.id
            session["twofactor_since"] = datetime.now(timezone.utc).timestamp()
            return redirect(url_for("login_2fa"))

        login_user_bundle(form.user)

        UserController(current_user.id).update(
            {"id": current_user.id}, {"last_seen": datetime.now(timezone.utc)}
        )

        return form.redirect("home")

    return render_template(
        "login.html",
        form=form,
        self_registration=application.config["SELF_REGISTRATION"],
    )


TWOFACTOR_TIMEOUT = 300  # seconds granted to enter the second factor


@current_app.route("/login/2fa", methods=["GET", "POST"])
def login_2fa():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    user_id = session.get("twofactor_user_id")
    since = session.get("twofactor_since", 0)
    elapsed = datetime.now(timezone.utc).timestamp() - since
    if user_id is None or elapsed > TWOFACTOR_TIMEOUT:
        session.pop("twofactor_user_id", None)
        session.pop("twofactor_since", None)
        flash(gettext("Your login attempt has expired. Please sign in again."), "info")
        return redirect(url_for("login"))

    ucontr = UserController(user_id, ignore_context=True)
    try:
        user = ucontr.get(id=user_id, is_active=True)
    except NotFound:
        session.pop("twofactor_user_id", None)
        session.pop("twofactor_since", None)
        return redirect(url_for("login"))

    form = TwoFactorForm()
    if request.method == "POST" and form.validate():
        counter = twofactor.verify_totp(user, form.code.data)
        if counter is not None:
            # remember the accepted timestep so the same code cannot be replayed
            ucontr.update({"id": user.id}, {"last_totp": counter})
            return complete_2fa_login(user)

        remaining_codes = twofactor.consume_recovery_code(user, form.code.data)
        if remaining_codes is not None:
            ucontr.update({"id": user.id}, {"recovery_codes": remaining_codes})
            flash(
                gettext(
                    "You have %(nb)d recovery code(s) left.",
                    nb=len(json.loads(remaining_codes)),
                ),
                "warning",
            )
            return complete_2fa_login(user)

        flash(gettext("Invalid code."), "danger")

    return render_template("login_2fa.html", form=form)


def complete_2fa_login(user):
    session.pop("twofactor_user_id", None)
    session.pop("twofactor_since", None)
    login_user_bundle(user)
    UserController(user.id).update(
        {"id": user.id}, {"last_seen": datetime.now(timezone.utc)}
    )
    return redirect(url_for("home"))


@current_app.route("/logout")
@login_required
def logout():
    # Remove the user information from the session
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ("identity.name", "identity.auth_type"):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app, identity=AnonymousIdentity())
    session_identity_loader()

    return redirect(url_for("login"))


@current_app.route("/signup", methods=["GET", "POST"])
def signup():
    if not application.config["SELF_REGISTRATION"]:
        flash(gettext("Self-registration is disabled."), "warning")
        return redirect(url_for("home"))
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = SignupForm()
    if form.validate_on_submit():
        user = UserController().create(
            nickname=form.nickname.data,
            pwdhash=generate_password_hash(form.password.data),
        )

        # Send the confirmation email
        try:
            notifications.new_account_notification(user, form.email.data)
        except Exception as error:
            flash(
                gettext(
                    "Problem while sending activation email: %(error)s", error=error
                ),
                "danger",
            )
            return redirect(url_for("home"))

        flash(
            gettext("Your account has been created. Check your mail to confirm it."),
            "success",
        )

        return redirect(url_for("home"))

    return render_template("signup.html", form=form)

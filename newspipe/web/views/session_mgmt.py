import logging
from datetime import datetime

from werkzeug.exceptions import NotFound
from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_babel import gettext, lazy_gettext
from flask_login import LoginManager, current_user, login_required, logout_user
from flask_principal import (
    AnonymousIdentity,
    Principal,
    UserNeed,
    identity_changed,
    identity_loaded,
    session_identity_loader,
)
from werkzeug.security import generate_password_hash

from newspipe.bootstrap import application
from newspipe.controllers import UserController
from newspipe.notifications import notifications
from newspipe.web.forms import SigninForm, SignupForm
from newspipe.web.views.common import admin_role, api_role, login_user_bundle

Principal(current_app)
# Create a permission with a single Need, in this case a RoleNeed.

login_manager = LoginManager()
login_manager.init_app(current_app)
login_manager.login_view = "login"
login_manager.login_message = ""
# login_manager.login_message_category = "info"

logger = logging.getLogger(__name__)


@identity_loaded.connect_via(current_app._get_current_object())
def on_identity_loaded(sender, identity):
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
        return UserController(user_id, ignore_context=True).get(id=user_id, is_active=True)
    except NotFound:
        pass


@current_app.before_request
def before_request():
    if current_user.is_authenticated:
        UserController(current_user.id).update(
            {"id": current_user.id}, {"last_seen": datetime.utcnow()}
        )


@current_app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = SigninForm()
    if form.validate_on_submit():
        login_user_bundle(form.user)
        return form.redirect("home")
    return render_template("login.html", form=form)


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
            gettext("Your account has been created. " "Check your mail to confirm it."),
            "success",
        )

        return redirect(url_for("home"))

    return render_template("signup.html", form=form)

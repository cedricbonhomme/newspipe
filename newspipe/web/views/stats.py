from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from newspipe.controllers import ArticleController

stats_bp = Blueprint("stats", __name__, url_prefix="/stats")


@stats_bp.route("/history.json", methods=["GET"])
@stats_bp.route("/history.json/<int:year>", methods=["GET"])
@stats_bp.route("/history.json/<int:year>/<int:month>", methods=["GET"])
@login_required
def history(year=None, month=None):
    cntr, _ = ArticleController(current_user.id).get_history(year, month)
    return jsonify(cntr)

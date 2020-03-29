import base64

from flask import Blueprint, Response, request

from newspipe.controllers import IconController
from newspipe.web.lib.view_utils import etag_match

icon_bp = Blueprint("icon", __name__, url_prefix="/icon")


@icon_bp.route("/", methods=["GET"])
@etag_match
def icon():
    try:
        icon = IconController().get(url=request.args["url"])
        headers = {"Cache-Control": "max-age=86400", "Content-Type": icon.mimetype}
        return Response(base64.b64decode(icon.content), headers=headers)
    except:
        headers = {"Cache-Control": "max-age=86400", "Content-Type": "image/gif"}
        return Response(base64.b64decode("R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=="), headers=headers)

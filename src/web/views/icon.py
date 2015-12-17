import base64
from flask import Blueprint, Response, request
from web.controllers import IconController
from web.lib.view_utils import etag_match

icon_bp = Blueprint('icon', __name__, url_prefix='/icon')

@icon_bp.route('/', methods=['GET'])
@etag_match
def icon():
    icon = IconController().get(url=request.args['url'])
    headers = {'Cache-Control': 'max-age=86400',
               'Content-Type': icon.mimetype}
    return Response(base64.b64decode(icon.content), headers=headers)

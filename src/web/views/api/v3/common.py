from flask.ext.login import current_user
from web.controllers import ArticleController


def is_authorized_to_modify(user, obj):
    return user.id == obj.user_id


def check_auth(instance_id=None, **kw):
    # Check if the user is authorized to modify the specified
    # instance of the model.
    contr = ArticleController(current_user.id)
    article = contr.get(id=instance_id)
    if not is_authorized_to_modify(current_user, article):
        raise ProcessingException(description='Not Authorized',
                                  code=401)

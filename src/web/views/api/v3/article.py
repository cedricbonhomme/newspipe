from web import models
from bootstrap import application, manager
from web.views.api.v3.common import url_prefix, auth_func
from web.views.api.v3.common import get_single_preprocessor, get_many_preprocessor


blueprint_article = manager.create_api_blueprint(models.Article,
        url_prefix=url_prefix,
        methods=['GET', 'POST', 'PUT', 'DELETE'],
        preprocessors=dict(GET_SINGLE=[auth_func, get_single_preprocessor],
                           GET_MANY=[auth_func, get_many_preprocessor],
                           PUT_SINGLE=[auth_func],
                           POST=[auth_func],
                           DELETE=[auth_func]))
application.register_blueprint(blueprint_article)

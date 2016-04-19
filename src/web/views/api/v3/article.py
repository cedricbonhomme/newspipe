from web import models
from bootstrap import application, manager
from web.views.api.v3.common import url_prefix, auth_func, check_auth


blueprint_article = manager.create_api_blueprint(models.Article,
                        url_prefix=url_prefix,
                        methods=['GET', 'POST', 'PUT', 'DELETE'],
                        preprocessors=dict(GET_SINGLE=[auth_func, check_auth]))
application.register_blueprint(blueprint_article)

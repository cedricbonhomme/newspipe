from flask.ext.login import current_user
from werkzeug.exceptions import NotFound
from flask.ext.restless import ProcessingException
from web import models
from bootstrap import application, manager
from web.controllers import ArticleController, FeedController
from web.views.api.v3.common import AbstractProcessor
from web.views.api.v3.common import url_prefix, auth_func

class ArticleProcessor(AbstractProcessor):
    """Concrete processors for the Article Web service.
    """

    def get_single_preprocessor(self, instance_id=None, **kw):
        article = ArticleController(current_user.id).get(id=instance_id)
        self.is_authorized(current_user, article)

    def post_preprocessor(self, data=None, **kw):
        data["user_id"] = current_user.id

        try:
            feed = FeedController(current_user.id).get(id=data["feed_id"])
        except NotFound:
            raise ProcessingException(description='No such feed.', code=404)
        self.is_authorized(current_user, feed)

        data["category_id"] = feed.category_id

    def delete_preprocessor(self, instance_id=None, **kw):
        try:
            article = ArticleController(current_user.id).get(id=instance_id)
        except NotFound:
            raise ProcessingException(description='No such article.', code=404)
        self.is_authorized(current_user, article)

article_processor = ArticleProcessor()

blueprint_article = manager.create_api_blueprint(models.Article,
        url_prefix=url_prefix,
        methods=['GET', 'POST', 'PUT', 'DELETE'],
        preprocessors=dict(GET_SINGLE=[auth_func,
                                    article_processor.get_single_preprocessor],
                            GET_MANY=[auth_func,
                                    article_processor.get_many_preprocessor],
                            POST=[auth_func,
                                    article_processor.post_preprocessor],
                            PUT_SINGLE=[auth_func,
                                    article_processor.put_single_preprocessor],
                            DELETE=[auth_func,
                                    article_processor.delete_preprocessor]))
application.register_blueprint(blueprint_article)

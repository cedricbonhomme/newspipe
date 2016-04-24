from flask.ext.login import current_user
from werkzeug.exceptions import NotFound
from flask.ext.restless import ProcessingException
from web import models
from bootstrap import application, manager
from web.controllers import ArticleController, FeedController
from web.views.api.v3.common import AbstractProcessor
from web.views.api.v3.common import url_prefix, auth_func

class ArticleProcessor(AbstractProcessor):
    def get_single_preprocessor(self, instance_id=None, **kw):
        # Check if the user is authorized to modify the specified
        # instance of the model.
        contr = ArticleController(current_user.id)
        article = contr.get(id=instance_id)
        if not self.is_authorized_to_modify(current_user, article):
            raise ProcessingException(description='Not Authorized', code=401)

    def post_put_preprocessor(self, data=None, **kw):
        data["user_id"] = current_user.id

        fcontr = FeedController()
        try:
            feed = fcontr.get(id=data["feed_id"])
        except NotFound:
            raise ProcessingException(description='No such feed.', code=404)

        data["category_id"] = feed.category_id

    def delete_preprocessor(self, instance_id=None, **kw):
        contr = ArticleController()
        try:
            article = contr.get(id=instance_id)
        except NotFound:
            raise ProcessingException(description='No such article.', code=404)
        if article.user_id != current_user.id:
            raise ProcessingException(description='Not Authorized', code=401)


article_processor = ArticleProcessor()

blueprint_article = manager.create_api_blueprint(models.Article,
        url_prefix=url_prefix,
        methods=['GET', 'POST', 'PUT', 'DELETE'],
        preprocessors=dict(GET_SINGLE=[auth_func,
                                    article_processor.get_single_preprocessor],
                            GET_MANY=[auth_func,
                                    article_processor.get_many_preprocessor],
                            POST=[auth_func,
                                    article_processor.post_put_preprocessor],
                            PUT_SINGLE=[auth_func,
                                    article_processor.post_put_preprocessor],
                            DELETE=[auth_func,
                                    article_processor.delete_preprocessor]))
application.register_blueprint(blueprint_article)

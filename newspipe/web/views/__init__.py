from web.views.api import v2, v3
from web.views import views, home, session_mgmt
from web.views.article import article_bp, articles_bp
from web.views.feed import feed_bp, feeds_bp
from web.views.category import category_bp, categories_bp
from web.views.icon import icon_bp
from web.views.admin import admin_bp
from web.views.user import user_bp, users_bp
from web.views.bookmark import bookmark_bp, bookmarks_bp

__all__ = ['views', 'home', 'session_mgmt', 'v2', 'v3',
           'article_bp', 'articles_bp', 'feed_bp', 'feeds_bp',
           'category_bp', 'categories_bp', 'icon_bp',
           'admin_bp', 'user_bp', 'users_bp', 'bookmark_bp', 'bookmarks_bp']

import conf
from flask import request
from flask import g


@g.babel.localeselector
def get_locale():
    return request.accept_languages.best_match(conf.LANGUAGES.keys())

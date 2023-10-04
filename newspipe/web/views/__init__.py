from newspipe.web.views import home, session_mgmt, views
from newspipe.web.views.admin import admin_bp
from newspipe.web.views.api import v2
from newspipe.web.views.article import article_bp, articles_bp
from newspipe.web.views.bookmark import bookmark_bp, bookmarks_bp
from newspipe.web.views.category import categories_bp, category_bp
from newspipe.web.views.feed import feed_bp, feeds_bp
from newspipe.web.views.icon import icon_bp
from newspipe.web.views.stats import stats_bp
from newspipe.web.views.user import user_bp

__all__ = [
    "home",
    "session_mgmt",
    "views",
    "admin_bp",
    "v2",
    "article_bp",
    "articles_bp",
    "bookmark_bp",
    "bookmarks_bp",
    "categories_bp",
    "category_bp",
    "feed_bp",
    "feeds_bp",
    "icon_bp",
    "user_bp",
    "stats_bp",
]

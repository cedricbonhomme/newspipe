from newspipe.web.views import home
from newspipe.web.views import session_mgmt
from newspipe.web.views import views
from newspipe.web.views.admin import admin_bp
from newspipe.web.views.api import v2
from newspipe.web.views.article import article_bp
from newspipe.web.views.article import articles_bp
from newspipe.web.views.bookmark import bookmark_bp
from newspipe.web.views.bookmark import bookmarks_bp
from newspipe.web.views.category import categories_bp
from newspipe.web.views.category import category_bp
from newspipe.web.views.feed import feed_bp
from newspipe.web.views.feed import feeds_bp
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

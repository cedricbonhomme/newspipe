import os

#
# Example configuration file for a SQLite database.
#

# Webserver
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True
API_ROOT = "/api/v2.0"

CSRF_ENABLED = True
SECRET_KEY = "LCx3BchmHRxFzkEv4BqQJyeXRLXenf"
SECURITY_PASSWORD_SALT = "L8gTsyrpRQEF8jNWQPyvRfv7U5kJkD"

# Database
SQLALCHEMY_DATABASE_URI = "sqlite:///newspipe.db"

# Security
CONTENT_SECURITY_POLICY = {
}

# Crawler
CRAWLING_METHOD = "default"
DEFAULT_MAX_ERROR = 6
HTTP_PROXY = ""
CRAWLER_USER_AGENT = "Newspipe (https://git.sr.ht/~cedric/newspipe)"
CRAWLER_TIMEOUT = 30
CRAWLER_RESOLVE_ARTICLE_URL = False
FEED_REFRESH_INTERVAL = 0

# Notification
MAIL_SERVER = "localhost"
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_DEBUG = DEBUG
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_DEFAULT_SENDER = "admin@admin.localhost"
TOKEN_VALIDITY_PERIOD = 3600
PLATFORM_URL = "https://www.newspipe.org"

# Misc
BASE_DIR = os.path.abspath(os.path.dirname("."))
LANGUAGES = {"en": "English", "fr": "French"}
TIME_ZONE = {"en": "US/Eastern", "fr": "Europe/Paris"}
ADMIN_EMAIL = "admin@admin.localhost"
LOG_LEVEL = "info"
LOG_PATH = "./var/newspipe.log"
SELF_REGISTRATION = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

import os

# Webserver
HOST = "127.0.0.1"
PORT = 5000
DEBUG = False
API_ROOT = "/api/v2.0"

CSRF_ENABLED = True
SECRET_KEY = "LCx3BchmHRxFzkEv4BqQJyeXRLXenf"
SECURITY_PASSWORD_SALT = "L8gTsyrpRQEF8jNWQPyvRfv7U5kJkD"
TOKEN_VALIDITY_PERIOD = 3600

# Database
DB_CONFIG_DICT = {
    "user": "user",
    "password": "password",
    "host": "localhost",
    "port": 5432,
}
DATABASE_NAME = "newspipe"
SQLALCHEMY_DATABASE_URI = "postgres://{user}:{password}@{host}:{port}/{name}".format(
    name=DATABASE_NAME, **DB_CONFIG_DICT
)

# Crawler
CRAWLING_METHOD = "default"
DEFAULT_MAX_ERROR = 3
HTTP_PROXY = ""
CRAWLER_USER_AGENT = "Newspipe (https://git.sr.ht/~cedric/newspipe)"
CRAWLER_TIMEOUT = 30
CRAWLER_RESOLV = False
RESOLVE_ARTICLE_URL = False
FEED_REFRESH_INTERVAL = 120

# Notification
MAIL_SERVER = "localhost"
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_DEBUG = DEBUG
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_DEFAULT_SENDER = ADMIN_EMAIL

# Misc
BASE_DIR = os.path.abspath(os.path.dirname('.'))
LANGUAGES = {"en": "English", "fr": "French"}
TIME_ZONE = {"en": "US/Eastern", "fr": "Europe/Paris"}
ADMIN_EMAIL = "admin@admin.localhost"
LOG_LEVEL = "info"
LOG_PATH = "./var/newspipe.log"
SELF_REGISTRATION = True

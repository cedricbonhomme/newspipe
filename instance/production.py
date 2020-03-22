import os

#
# Example configuration file for a PostgreSQL database.
#

# Webserver
HOST = "0.0.0.0"
PORT = 5000
DEBUG = False
API_ROOT = "/api/v2.0"

CSRF_ENABLED = True
SECRET_KEY = "LCx3BchmHRxFzkEv4BqQJyeXRLXenf"
SECURITY_PASSWORD_SALT = "L8gTsyrpRQEF8jNWQPyvRfv7U5kJkD"

# Database
DB_CONFIG_DICT = {
    "user": "postgres",
    "password": "password",
    "host": "db",
    "port": 5432,
}
DATABASE_NAME = "postgres"
SQLALCHEMY_DATABASE_URI = "postgres://{user}:{password}@{host}:{port}/{name}".format(
    name=DATABASE_NAME, **DB_CONFIG_DICT
)

# Security
CONTENT_SECURITY_POLICY = {
    'default-src': '\'self\'',
    'img-src': '*',
    'media-src': [
        'youtube.com',
    ],
    'script-src': [
        '\'self\'',
        '\'unsafe-inline\'',
    ],
    'style-src': [
        '\'self\'',
        '\'unsafe-inline\'',
    ]
}
# Crawler
CRAWLING_METHOD = "default"
DEFAULT_MAX_ERROR = 6
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

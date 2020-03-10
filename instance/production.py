# webserver
HOST = "127.0.0.1"
PORT = 5000
DEBUG = False
TESTING = False
API_ROOT = "/api/v2.0"

SECRET_KEY = "LCx3BchmHRxFzkEv4BqQJyeXRLXenf"
SECURITY_PASSWORD_SALT = "L8gTsyrpRQEF8jNWQPyvRfv7U5kJkD"


# misc
ADMIN_EMAIL = "admin@admin.localhost"
TOKEN_VALIDITY_PERIOD = 3600
LOG_LEVEL = "info"
LOG_PATH = "./var/newspipe.log"
NB_WORKER = 5
SELF_REGISTRATION = True


# database
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
SQLALCHEMY_TRACK_MODIFICATIONS = False


# crawler
CRAWLING_METHOD = "default"
DEFAULT_MAX_ERROR = 3
HTTP_PROXY = ""
USER_AGENT = "Newspipe (https://git.sr.ht/~cedric/newspipe)"
RESOLVE_ARTICLE_URL = False
TIMEOUT = 30
RESOLV = False
FEED_REFRESH_INTERVAL = 0


# notification
MAIL_SERVER = "localhost"
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_DEBUG = DEBUG
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_DEFAULT_SENDER = ADMIN_EMAIL

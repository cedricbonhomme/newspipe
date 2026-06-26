import os

#
# Example configuration file for a SQLite database.
#

# Webserver
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True
API_ROOT = "/api/v2.0"

# Optional, and useful if you are using a reverse proxy with this virtual path prefix
# PREFIX = "/newspipe"

CSRF_ENABLED = True
SECRET_KEY = "LCx3BchmHRxFzkEv4BqQJyeXRLXenf"
SECURITY_PASSWORD_SALT = "L8gTsyrpRQEF8jNWQPyvRfv7U5kJkD"

# Database
# Use an absolute path derived from this config file's own location (the instance
# directory) so the database resolves to the same file whether loaded by the app
# or the flask CLI, regardless of the current working directory.
_INSTANCE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(_INSTANCE_DIR, "newspipe.db")

# Security
CONTENT_SECURITY_POLICY = {
    "default-src": "'self'",
    "img-src": "* data:",
    "media-src": [
        "'self'",
        "https:",
    ],
    "script-src": [
        "'self'",
        "'unsafe-inline'",
    ],
    "style-src": [
        "'self'",
        "'unsafe-inline'",
    ],
}

# Crawler
CRAWLING_METHOD = "default"
DEFAULT_MAX_ERROR = 6
HTTP_PROXY = ""
CRAWLER_USER_AGENT = "Newspipe (https://github.com/cedricbonhomme/newspipe)"
CRAWLER_TIMEOUT = 30
CRAWLER_RESOLVE_ARTICLE_URL = False
# Maximum number of feeds fetched concurrently.
CRAWLER_MAX_CONCURRENCY = 10
# Maximum feed body size accepted by the crawler, in bytes (default 10 MiB).
# Larger responses are rejected to avoid exhausting memory.
CRAWLER_MAX_FEED_SIZE = 10 * 1024 * 1024
FEED_REFRESH_INTERVAL = 0
# Number of days before a feed auto-disabled (after DEFAULT_MAX_ERROR errors)
# is retried, in case the source has recovered.
DISABLED_FEED_RETRY_INTERVAL = 7

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

# Ldap, optional
LDAP_ENABLED = False
# LDAP_URI will automatically try the _ldap._tcp lookups like for a kerberos domain but
# will fall back to this exact domain (server) name if such a TXT record is not found.
LDAP_URI = "ldaps://ipa.internal.com:636"
LDAP_USER_BASE = "cn=users,cn=accounts,dc=ipa,dc=internal,dc=com"
LDAP_GROUP_BASE = "cn=groups,cn=accounts,dc=ipa,dc=internal,dc=com"
LDAP_USER_MATCH_ATTRIB = "uid"
LDAP_USER_DISPLAY_ATTRIB = "uid"
LDAP_USER_ATTRIB_MEMBEROF = "memberof"
LDAP_GROUP_DISPLAY_ATTRIB = "cn"
LDAP_BIND_DN = "uid=sampleuser,cn=users,cn=accounts,dc=ipa,dc=internal,dc=com"
LDAP_BIND_PASSWORD = "examplepassword"
# Additional filter to restrict user lookup. If not equivalent to False
# (e.g., undefined), will be logical-anded to the user-match-attribute search filter.
LDAP_FILTER = (
    "(memberOf=cn=newspipe-users,cn=groups,cn=accounts,dc=ipa,dc=internal,dc=com)"
)


VULNERABILITY_LOOKUP_BASE_URL = "https://vulnerability.circl.lu/"
VULNERABILITY_AUTH_TOKEN = ""

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
SQLALCHEMY_DATABASE_URI = "sqlite:///newspipe.db"

# Security
CONTENT_SECURITY_POLICY = {
    "default-src": "'self'",
    "img-src": "* data:",
    "media-src": [
        "youtube.com",
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

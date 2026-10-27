import os

#
# Example configuration file for a SQLite database.
#

# Web server
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True
API_ROOT = "/api/v2.0"
# Optional, and useful if you are using a reverse proxy with this virtual path prefix
# PREFIX = "/newspipe"
# Public address of the instance, used in the links sent by email.
PLATFORM_URL = "https://www.newspipe.org"

# Database
# Use an absolute path derived from this config file's own location (the instance
# directory) so the database resolves to the same file whether loaded by the app
# or the flask CLI, regardless of the current working directory.
_INSTANCE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(_INSTANCE_DIR, "newspipe.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Security
SECRET_KEY = "LCx3BchmHRxFzkEv4BqQJyeXRLXenf"
SECURITY_PASSWORD_SALT = "L8gTsyrpRQEF8jNWQPyvRfv7U5kJkD"
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
# Issuer name displayed in the two-factor authentication application of the
# users (below the TOTP code). It is recommended to use the public address of
# your instance: users having accounts on several Newspipe instances will
# easily find the right entry.
TOTP_ISSUER = "www.newspipe.org"

# Users and access
ADMIN_EMAIL = "admin@admin.localhost"
SELF_REGISTRATION = True
# Validity period of the account activation tokens, in seconds.
TOKEN_VALIDITY_PERIOD = 3600
# Require authentication to see the popular feeds page (/popular), the
# bookmarks page (/bookmarks) and the public profile pages of the users
# with the public feeds, articles and categories they expose
# (/user/<nickname>, /user/<nickname>/stream, /feed/public/<id>,
# /article/public/<id> and /category/<id>).
PROTECT_POPULAR_PAGE = False
PROTECT_BOOKMARKS_PAGE = False
PROTECT_USER_PAGES = False
# Let search engines index the public pages of the instance (home, about,
# login, sign up, popular feeds) and describe Newspipe with structured data.
# Private pages are never indexed. Leave disabled for a private instance.
SEARCH_ENGINE_INDEXING = False

# LDAP authentication, optional
LDAP_ENABLED = False
# LDAP_URI will automatically try the _ldap._tcp lookups like for a kerberos domain but
# will fall back to this exact domain (server) name if such a TXT record is not found.
LDAP_URI = "ldaps://ipa.internal.com:636"
LDAP_USER_BASE = "cn=users,cn=accounts,dc=ipa,dc=internal,dc=com"
LDAP_USER_MATCH_ATTRIB = "uid"
LDAP_BIND_DN = "uid=sampleuser,cn=users,cn=accounts,dc=ipa,dc=internal,dc=com"
LDAP_BIND_PASSWORD = "examplepassword"
# Additional filter to restrict user lookup. If not equivalent to False
# (e.g., undefined), will be logical-anded to the user-match-attribute search filter.
LDAP_FILTER = (
    "(memberOf=cn=newspipe-users,cn=groups,cn=accounts,dc=ipa,dc=internal,dc=com)"
)

# Crawler
CRAWLING_METHOD = "default"
CRAWLER_USER_AGENT = "Newspipe (https://sr.ht/~cedric/newspipe)"
CRAWLER_TIMEOUT = 30
CRAWLER_RESOLVE_ARTICLE_URL = False
# Maximum number of feeds fetched concurrently.
CRAWLER_MAX_CONCURRENCY = 10
# Maximum feed body size accepted by the crawler, in bytes (default 10 MiB).
# Larger responses are rejected to avoid exhausting memory.
CRAWLER_MAX_FEED_SIZE = 10 * 1024 * 1024
FEED_REFRESH_INTERVAL = 0
# Number of errors after which a feed is automatically disabled.
DEFAULT_MAX_ERROR = 6
# Number of days before a feed auto-disabled (after DEFAULT_MAX_ERROR errors)
# is retried, in case the source has recovered.
DISABLED_FEED_RETRY_INTERVAL = 7

# Import
# Maximum size of an uploaded OPML file, in bytes (default 5 MiB). A
# subscription list with 10,000 feeds stays well under 1 MiB.
OPML_MAX_SIZE = 5 * 1024 * 1024

# Notifications (email)
MAIL_SERVER = "localhost"
MAIL_PORT = 25
# Use STARTTLS (usually on port 587) or implicit TLS (usually on port 465).
# The certificate of the server is verified. Enable at most one of them.
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_DEFAULT_SENDER = "admin@admin.localhost"

# Vulnerability Lookup
VULNERABILITY_LOOKUP_BASE_URL = "https://vulnerability.circl.lu/"
VULNERABILITY_AUTH_TOKEN = ""

# Misc
BASE_DIR = os.path.abspath(os.path.dirname("."))
LANGUAGES = {"en": "English", "fr": "French", "de": "German"}
LOG_PATH = "./var/newspipe.log"

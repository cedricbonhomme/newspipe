# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Newspipe is a web news aggregator written in Python using Flask, asyncio, and SQLAlchemy. It supports multiple users, RSS/Atom feed crawling, article management, bookmarks, and optional LDAP authentication.

## Essential Commands

### Initial Setup

```bash
# Install dependencies
npm ci
poetry install

# Compile translations
pybabel compile -d newspipe/translations

# Database initialization (SQLite)
export NEWSPIPE_CONFIG=sqlite.py
flask db_init
flask create_admin --nickname <nickname> --password <password>

# Database initialization (PostgreSQL)
export NEWSPIPE_CONFIG=postgresql.py
flask db_create
flask db_init
```

### Development

```bash
# Run development server
flask run --debug

# Run feed crawler manually
flask fetch_asyncio

# Run crawler for specific user or feed
flask fetch_asyncio --user-id <id>
flask fetch_asyncio --feed-id <id>
```

### Database Management

```bash
# Run database migrations
flask db upgrade

# Empty database (drops all data)
flask db_empty
```

### Code Quality

```bash
# Format code with black
black .

# Run flake8 linting (max line length: 125)
flake8 --max-line-length=125

# Run type checking
mypy

# Run pre-commit hooks
pre-commit run --all-files
```

### User Management

```bash
# Create admin user
flask create_admin --nickname <nickname> --password <password>

# Delete user
flask delete_user --user-id <id>

# Delete inactive users (default: 6 months)
flask delete_inactive_users --last-seen <months>

# Disable inactive users
flask disable_inactive_users --last-seen <months>
```

### Article and Feed Management

```bash
# Delete read articles (older than 60 days)
flask delete_read_articles

# Find vulnerabilities in articles
flask find_vulnerabilities --user-id <id> --category-id <id> --sighting-type <type>
```

## Architecture

### Core Structure

```
newspipe/
├── bootstrap.py           # Flask app initialization, DB setup, i18n
├── commands.py            # Flask CLI commands
├── models/                # SQLAlchemy ORM models
│   ├── user.py           # User model
│   ├── feed.py           # Feed model
│   ├── article.py        # Article model
│   ├── category.py       # Category model
│   ├── bookmark.py       # Bookmark model
│   ├── icon.py           # Feed icon model
│   └── tag.py            # Tag models (ArticleTag, BookmarkTag)
├── controllers/           # Data access layer (CRUD operations)
│   ├── abstract.py       # Base controller with filtering and rights management
│   ├── user.py           # UserController
│   ├── feed.py           # FeedController
│   ├── article.py        # ArticleController
│   ├── category.py       # CategoryController
│   ├── bookmark.py       # BookmarkController
│   └── icon.py           # IconController
├── web/
│   ├── views/            # Flask blueprints for web UI
│   │   ├── home.py       # Home page
│   │   ├── feed.py       # Feed management views
│   │   ├── article.py    # Article views
│   │   ├── category.py   # Category views
│   │   ├── bookmark.py   # Bookmark views
│   │   ├── user.py       # User profile views
│   │   ├── admin.py      # Admin views
│   │   ├── session_mgmt.py  # Authentication
│   │   └── api/v2/       # RESTful API endpoints
│   ├── forms.py          # WTForms definitions
│   ├── decorators.py     # View decorators (auth, admin checks)
│   └── lib/              # Web utilities
├── crawler/
│   └── default_crawler.py  # Asyncio-based feed crawler
├── lib/                  # Core utilities
│   ├── article_utils.py  # Article processing
│   ├── feed_utils.py     # Feed processing
│   ├── sanitizers.py     # HTML sanitization
│   └── utils.py          # General utilities
└── notifications/        # Email notifications
```

### Key Patterns

**Controllers**: All database operations go through controllers (in `newspipe/controllers/`). Controllers inherit from `AbstractController` which provides:
- User-scoped filtering (filters objects by `user_id`)
- CRUD operations with rights management
- Filter syntax with operators: `__gt`, `__lt`, `__ge`, `__le`, `__ne`, `__in`, `__like`, `__ilike`, `__contains`

**Example controller usage**:
```python
from newspipe.controllers import ArticleController

# Get articles for a user
article_ctrl = ArticleController(user_id=user.id)
articles = article_ctrl.read(readed=False, feed_id__in=[1, 2, 3]).all()

# Create an article
article = article_ctrl.create(
    title="Example", content="Content", feed_id=feed_id, commit=True
)
```

**Models**: SQLAlchemy models in `newspipe/models/` define database schema. Key relationships:
- User has many Feeds
- Feed has many Articles and belongs to one Category
- Article has many Tags
- User has many Bookmarks

**Views**: Flask blueprints in `newspipe/web/views/` handle HTTP requests. Web UI views use Jinja2 templates. API views (in `api/v2/`) use Flask-RESTful.

**Crawler**: The async crawler (`newspipe/crawler/default_crawler.py`) uses `asyncio` with `aiohttp` to fetch feeds. It's invoked via `flask fetch_asyncio` and typically scheduled with cron.

## Configuration

Configuration files live in `instance/`:
- `sqlite.py` - SQLite configuration (default)
- `config.py` - PostgreSQL configuration example

Set the config via environment variable:
```bash
export NEWSPIPE_CONFIG=sqlite.py  # or postgresql.py
```

Key configuration sections:
- Database: `SQLALCHEMY_DATABASE_URI`, `DB_CONFIG_DICT`
- Security: `CONTENT_SECURITY_POLICY`, `SECRET_KEY`, `CSRF_ENABLED`
- Crawler: `CRAWLER_USER_AGENT`, `CRAWLER_TIMEOUT`, `FEED_REFRESH_INTERVAL`
- LDAP: `LDAP_ENABLED`, `LDAP_URI`, `LDAP_USER_BASE` (optional)
- Vulnerability Lookup: `VULNERABILITY_LOOKUP_BASE_URL` (integration with vulnerability.circl.lu)

## Database Migrations

Uses Flask-Migrate (Alembic). Migration files are in `migrations/versions/`.

```bash
# Apply migrations
flask db upgrade

# Create a new migration
flask db migrate -m "Description"
```

## Frontend

Frontend uses:
- Bootstrap 5 for UI
- Chart.js for visualizations
- Moment.js/Luxon for date handling
- Node modules are symlinked to `newspipe/static/npm_components/` via postinstall script

Install frontend dependencies:
```bash
npm ci  # automatically runs postinstall to create symlink
```

## Testing and Code Style

The project uses:
- **black** for code formatting
- **flake8** for linting (max line length: 125)
- **mypy** for type checking (Python 3.13 target)
- **pre-commit** hooks for automated checks
- **isort** with black profile for import ordering

Pre-commit hooks run:
- pyupgrade (Python 3.7+ syntax)
- reorder-python-imports
- black
- flake8 with bugbear and implicit-str-concat plugins
- pip-audit for dependency vulnerability scanning

## API

RESTful API is available at `/api/v2.0/` with endpoints for:
- Articles: `/api/v2.0/article`
- Feeds: `/api/v2.0/feed`
- Categories: `/api/v2.0/category`

API authentication uses API tokens (users need `is_api=True` flag).

## Important Notes

- The project requires Python >= 3.10
- Minimum Poetry version 2.0 is required
- When modifying models, always create a migration
- All HTML content is sanitized using bleach (see `newspipe/lib/sanitizers.py`)
- The crawler runs asynchronously and should be scheduled via cron for production
- User context is managed via controllers - always use controllers for database access
- CSRF protection is enabled globally via Flask-WTF
- Content Security Policy is enforced via Flask-Talisman

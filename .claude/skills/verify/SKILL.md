---
name: verify
description: Build, launch, and drive Newspipe locally to verify a change end-to-end against the real HTTP surface.
---

# Verifying Newspipe changes

## Launch

```bash
export NEWSPIPE_CONFIG=sqlite.py        # uses instance/newspipe.db
poetry run flask db upgrade             # apply pending migrations
poetry run flask run --debug --port 5599
```

Gotcha: without `--debug`, Flask-Talisman 302-redirects every HTTP request
to HTTPS — curl/requests against `http://127.0.0.1` only work in debug mode.

## Test data

Create a throwaway user + feed + articles with the controllers (app context),
then drive over HTTP. Delete afterwards with `flask delete_user --user-id <id>`.

```python
from werkzeug.security import generate_password_hash
from newspipe.bootstrap import application
from newspipe.controllers import ArticleController, FeedController, UserController

with application.app_context():
    user = UserController(ignore_context=True).create(
        nickname="verifybot",
        pwdhash=generate_password_hash("verifypass123"),
        is_active=True,
        is_admin=False,
        is_api=False,
    )
    feed = FeedController(user.id).create(
        title="Verify Feed",
        link="http://example.com/feed",
        site_link="http://example.com",
    )
    ArticleController(user.id).create(
        entry_id="verify-0",
        title="Verify article",
        content="Content",
        link="http://example.com/0",
        feed_id=feed.id,
    )
```

Keep `is_api=False`: non-admin users with `is_api=True` hit a pre-existing
500 on `PUT /api/v2.0/article/<id>` (`_get_attrs_desc` chokes on the `tags`
association proxy in `fields_api_write`).

## Drive

- Login: GET `/login`, scrape `name="csrf_token" ... value="..."` from the
  form, POST nickname/password with it (requests.Session keeps the cookie).
- Pages needing CSRF from JS use the `<meta name="csrf-token">` tag in the
  layout; send it as an `X-CSRFToken` header.
- Useful surfaces: `/` (home, `?filter_=all|read|unread`, `?liked=1`,
  `?read_later=1`), `/home/articles` (infinite-scroll JSON),
  `/article/<id>`, `/api/v2.0/article/<id>` (basic auth works in debug).
- Badge assertion: `id="total-unread"` in the home HTML.

## Flows worth driving

Snooze/read/like toggles, mark_all_as_read, search (`?query=...&search_title=on
&search_content=on`), migration up/down/up (`flask db downgrade` / `upgrade`).

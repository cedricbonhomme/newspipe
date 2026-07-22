#! /usr/bin/env python
"""ASGI shell of the Strangler Fig modernization experiment.

FastAPI acts as the facade: the migrated endpoints (R1 feeds, R2 articles)
are served natively under the SAME prefix as the legacy v2 API, so API
consumers keep their URLs. Every other route (web UI, rest of the API) is
delegated unchanged to the legacy Flask application through the
ASGI-to-WSGI adapter.

Usage:
    NEWSPIPE_CONFIG=sqlite.py uvicorn asgi:app --port 8000
"""
from a2wsgi import WSGIMiddleware
from fastapi import FastAPI

import app as _legacy  # noqa: F401  (registers blueprints and the v2 API)
from newspipe.api_v3.articles import router as articles_router
from newspipe.api_v3.feeds import router as feeds_router
from newspipe.bootstrap import application as flask_app

API_PREFIX = flask_app.config.get("API_ROOT", "/api/v2.0")

app = FastAPI(
    title="Newspipe API (Strangler Fig facade)",
    description=(
        "Modernized endpoints served natively by FastAPI. "
        "Non-migrated routes are delegated to the legacy Flask application."
    ),
    version="experiment-1",
)

# Migrated endpoints (attended natively by FastAPI)
app.include_router(feeds_router, prefix=API_PREFIX)
app.include_router(articles_router, prefix=API_PREFIX)

# Everything else is delegated to the legacy Flask application
app.mount("/", WSGIMiddleware(flask_app))

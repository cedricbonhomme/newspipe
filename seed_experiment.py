#! /usr/bin/env python
"""Seed data for the modernization experiment (Strangler Fig, R1 feeds / R2 articles).

Creates two feeds and four articles for the admin user so that the legacy API
and the FastAPI increment can be compared against the same database.

Usage:
    NEWSPIPE_CONFIG=sqlite.py python seed_experiment.py
"""
from datetime import datetime

import app  # noqa: F401  (registers blueprints and the v2 API on the Flask app)
from newspipe.bootstrap import application
from newspipe.controllers import ArticleController
from newspipe.controllers import FeedController
from newspipe.controllers import UserController

FEEDS = [
    {
        "title": "CIRCL Newsroom",
        "description": "Computer Incident Response Center Luxembourg",
        "link": "https://www.circl.lu/rss.xml",
        "site_link": "https://www.circl.lu",
    },
    {
        "title": "Python Insider",
        "description": "Python core development news",
        "link": "https://pythoninsider.blogspot.com/feeds/posts/default",
        "site_link": "https://pythoninsider.blogspot.com",
    },
]

ARTICLES = [
    {
        "entry_id": "exp-001",
        "title": "Alerta de seguridad CIRCL",
        "link": "https://www.circl.lu/news/exp-001",
        "content": "Contenido de prueba del experimento (articulo 1).",
        "readed": False,
        "date": datetime(2026, 7, 1, 10, 0, 0),
    },
    {
        "entry_id": "exp-002",
        "title": "Boletin mensual CIRCL",
        "link": "https://www.circl.lu/news/exp-002",
        "content": "Contenido de prueba del experimento (articulo 2).",
        "readed": True,
        "date": datetime(2026, 7, 5, 9, 30, 0),
    },
    {
        "entry_id": "exp-003",
        "title": "Novedades de Python 3.14",
        "link": "https://pythoninsider.blogspot.com/exp-003",
        "content": "Contenido de prueba del experimento (articulo 3).",
        "readed": False,
        "date": datetime(2026, 7, 10, 15, 45, 0),
    },
    {
        "entry_id": "exp-004",
        "title": "Sprint de desarrollo de CPython",
        "link": "https://pythoninsider.blogspot.com/exp-004",
        "content": "Contenido de prueba del experimento (articulo 4).",
        "readed": True,
        "date": datetime(2026, 7, 15, 8, 20, 0),
    },
]


def seed():
    with application.app_context():
        admin = UserController(ignore_context=True).get(nickname="admin")
        fctrl = FeedController(admin.id)
        actrl = ArticleController(admin.id)

        existing = {feed.link for feed in fctrl.read()}
        feed_ids = []
        for feed in FEEDS:
            if feed["link"] in existing:
                feed_ids.append(fctrl.get(link=feed["link"]).id)
                print(f"Feed ya existe: {feed['title']}")
                continue
            created = fctrl.create(**feed)
            feed_ids.append(created.id)
            print(f"Feed creado: {created.title} (id={created.id})")

        existing_articles = {a.entry_id for a in actrl.read()}
        for i, art in enumerate(ARTICLES):
            if art["entry_id"] in existing_articles:
                print(f"Articulo ya existe: {art['entry_id']}")
                continue
            feed_id = feed_ids[0] if i < 2 else feed_ids[1]
            created = actrl.create(feed_id=feed_id, **art)
            print(f"Articulo creado: {created.title} (id={created.id})")


if __name__ == "__main__":
    seed()

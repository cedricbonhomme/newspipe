"""FastAPI increment of the Strangler Fig modernization experiment.

This package contains the modernized endpoints of the v2 API:
- R1: feed management (list and create) in ``feeds.py``
- R2: article management (list with filters and get by id) in ``articles.py``

The routers reuse the existing controllers and SQLAlchemy models of the
legacy application, so both the legacy and the modernized code operate on
the same database.
"""

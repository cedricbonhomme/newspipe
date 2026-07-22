"""Pydantic schemas of the FastAPI increment.

These schemas declare the API contract explicitly and replace the manual,
role-based argument parsing of ``web/views/api/v2/common.py``.
"""
from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class FeedIn(BaseModel):
    """Contract to create a feed (request body of POST /feed)."""

    title: str
    link: str
    description: str = ""
    site_link: str = ""
    enabled: bool = True
    category_id: int | None = None


class FeedOut(BaseModel):
    """Contract of a feed returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    link: str
    site_link: str
    enabled: bool
    private: bool
    user_id: int
    category_id: int | None = None
    created_date: datetime
    last_retrieved: datetime


class ArticleOut(BaseModel):
    """Contract of an article returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    entry_id: str
    title: str | None = None
    link: str | None = None
    content: str | None = None
    readed: bool
    like: bool
    date: datetime
    retrieved_date: datetime
    user_id: int
    feed_id: int
    category_id: int | None = None
    tags: list[str] = []

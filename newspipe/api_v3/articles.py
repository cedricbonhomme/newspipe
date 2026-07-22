"""R2 - Article management in FastAPI (list with filters and get by id).

Replaces the read operations of ``ArticlesAPI``/``ArticleAPI`` of the legacy
v2 API. The filters are declared as typed query parameters instead of being
parsed manually, and the business logic stays in ``ArticleController``.
"""
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from werkzeug.exceptions import Forbidden
from werkzeug.exceptions import NotFound

from newspipe.api_v3.deps import AuthUser
from newspipe.api_v3.deps import get_current_user
from newspipe.api_v3.schemas import ArticleOut
from newspipe.bootstrap import application
from newspipe.controllers import ArticleController

router = APIRouter(tags=["articles"])


def _controller(user: AuthUser) -> ArticleController:
    return ArticleController() if user.is_admin else ArticleController(user.id)


@router.get("/articles", response_model=list[ArticleOut])
def list_articles(
    feed_id: int | None = None,
    readed: bool | None = None,
    limit: int = 10,
    user: AuthUser = Depends(get_current_user),
) -> list[ArticleOut]:
    """List the articles of the authenticated user, with optional filters."""
    filters = {
        key: value
        for key, value in {"feed_id": feed_id, "readed": readed}.items()
        if value is not None
    }
    with application.app_context():
        query = _controller(user).read(**filters)
        if limit:
            query = query.limit(limit)
        return [ArticleOut.model_validate(article) for article in query]


@router.get("/article/{article_id}", response_model=ArticleOut)
def get_article(
    article_id: int,
    user: AuthUser = Depends(get_current_user),
) -> ArticleOut:
    """Retrieve a single article by its identifier."""
    with application.app_context():
        try:
            article = _controller(user).get(id=article_id)
        except NotFound:
            raise HTTPException(404, "Article not found")
        except Forbidden:
            raise HTTPException(403, "Not authorized to access this article")
        return ArticleOut.model_validate(article)

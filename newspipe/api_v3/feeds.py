"""R1 - Feed management in FastAPI (list and create).

Replaces ``FeedsAPI``/``FeedNewAPI`` of the legacy v2 API. The router only
declares the contract and the validation: the business logic stays in the
existing ``FeedController``.
"""
from fastapi import APIRouter
from fastapi import Depends

from newspipe.api_v3.deps import AuthUser
from newspipe.api_v3.deps import get_current_user
from newspipe.api_v3.deps import require_api_right
from newspipe.api_v3.schemas import FeedIn
from newspipe.api_v3.schemas import FeedOut
from newspipe.bootstrap import application
from newspipe.controllers import FeedController

router = APIRouter(tags=["feeds"])


def _controller(user: AuthUser) -> FeedController:
    # Same scoping rule as the legacy resource: admins get an unscoped
    # controller, regular users only see their own feeds.
    return FeedController() if user.is_admin else FeedController(user.id)


@router.get("/feeds", response_model=list[FeedOut])
def list_feeds(
    limit: int = 10,
    user: AuthUser = Depends(get_current_user),
) -> list[FeedOut]:
    """List the feeds of the authenticated user (default limit 10, as in v2)."""
    with application.app_context():
        query = _controller(user).read()
        if limit:
            query = query.limit(limit)
        return [FeedOut.model_validate(feed) for feed in query]


@router.post("/feed", response_model=FeedOut, status_code=201)
def create_feed(
    feed: FeedIn,
    user: AuthUser = Depends(require_api_right),
) -> FeedOut:
    """Create a feed for the authenticated user."""
    with application.app_context():
        controller = FeedController(user.id)
        created = controller.create(**feed.model_dump())
        return FeedOut.model_validate(created)

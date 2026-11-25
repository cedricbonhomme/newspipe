# ArticleController.update() must refuse to attach an article to a category
# owned by another user. The ownership check used to sit in a try/except that
# swallowed the failure, so the foreign category_id was saved anyway.
from types import SimpleNamespace

import pytest
from werkzeug.exceptions import Forbidden
from werkzeug.exceptions import NotFound

from newspipe.controllers import article as article_module
from newspipe.controllers.abstract import AbstractController
from newspipe.controllers.article import ArticleController

OWNER, OTHER = 101, 202
CATEGORIES = {
    1: SimpleNamespace(id=1, user_id=OWNER),
    2: SimpleNamespace(id=2, user_id=OTHER),
}


class FakeCategoryController:
    def __init__(self, user_id=None):
        pass

    def get(self, id):
        if id not in CATEGORIES:
            raise NotFound()
        return CATEGORIES[id]


@pytest.fixture
def saved(monkeypatch):
    """Stub the database: record what would have been persisted."""
    calls = []
    monkeypatch.setattr(article_module, "CategoryController", FakeCategoryController)
    monkeypatch.setattr(
        AbstractController,
        "update",
        lambda self, filters, attrs: calls.append(attrs) or 1,
    )
    return calls


def test_own_category_is_accepted(saved):
    assert ArticleController(OWNER).update({"id": 5}, {"category_id": 1}) == 1
    assert saved == [{"category_id": 1}]


def test_foreign_category_is_refused(saved):
    with pytest.raises(Forbidden):
        ArticleController(OWNER).update({"id": 5}, {"category_id": 2})
    assert saved == []


def test_unknown_category_is_refused(saved):
    with pytest.raises(NotFound):
        ArticleController(OWNER).update({"id": 5}, {"category_id": 999})
    assert saved == []


def test_admin_context_is_not_restricted(saved):
    """A controller without user_id is the internal "super user" mode."""
    ArticleController().update({"id": 5}, {"category_id": 2})
    assert saved == [{"category_id": 2}]


def test_update_without_category_skips_the_check(saved):
    ArticleController(OWNER).update({"id": 5}, {"readed": True})
    assert saved == [{"readed": True}]

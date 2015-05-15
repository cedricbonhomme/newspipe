from tests.base import BasePyaggTest
from pyaggr3g470r.controllers import ArticleController


class ArticleControllerTest(BasePyaggTest):
    _contr_cls = ArticleController

    def test_controller(self):
        article = ArticleController(2).read()[0].dump()
        self.assertFalse(article['readed'])
        article['readed'] = True  # article get read when retreived through get
        self._test_controller_rights(article, article['user_id'])
        self.assertEquals(0, len(list(ArticleController().challenge(
                [{'id': art.id} for art in ArticleController(3).read()]))))
        self.assertEquals(9, len(list(ArticleController(2).challenge(
                [{'id': art.id} for art in ArticleController(3).read()]))))
        self.assertEquals(9, len(list(ArticleController(2).challenge(
                [{'entry_id': art.id} for art in ArticleController(3).read()]
        ))))
        self.assertEquals({1: 2, 2: 3, 3: 3},
                ArticleController(2).get_unread())
        self.assertEquals({4: 3, 5: 3, 6: 3},
                ArticleController(3).get_unread())

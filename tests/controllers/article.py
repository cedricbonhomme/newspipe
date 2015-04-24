from tests.base import BasePyaggTest
from pyaggr3g470r.controllers import ArticleController


class ArticleControllerTest(BasePyaggTest):
    _contr_cls = ArticleController

    def test_controller(self):
        article = ArticleController(2).read()[0].dump()
        self.assertFalse(article['readed'])
        article['readed'] = True  # article get read when retreived through get
        self._test_controller_rights(article, article['user_id'])

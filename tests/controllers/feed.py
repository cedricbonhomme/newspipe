from tests.base import BasePyaggTest
from pyaggr3g470r.controllers import FeedController
from pyaggr3g470r.controllers import ArticleController


class FeedControllerTest(BasePyaggTest):
    _contr_cls = FeedController

    def test_controller(self):
        feed = FeedController(2).read()[0].dump()
        self.assertTrue(3, ArticleController().read(feed_id=feed['id']).count())
        self._test_controller_rights(feed, feed['user_id'])
        # checking articles are deleted after the feed has been deleted
        self.assertFalse(0,
                ArticleController().read(feed_id=feed['id']).count())

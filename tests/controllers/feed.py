from tests.base import BasePyaggTest
from pyaggr3g470r.controllers import FeedController
from pyaggr3g470r.controllers import ArticleController


class FeedControllerTest(BasePyaggTest):
    _contr_cls = FeedController

    def test_feed_rights(self):
        feed = FeedController(2).read()[0].dump()
        self.assertTrue(3,
                ArticleController().read(feed_id=feed['id']).count())
        self._test_controller_rights(feed, feed['user_id'])
        # checking articles are deleted after the feed has been deleted

    def test_feed_article_deletion(self):
        feed_ctr = FeedController(2)
        feed = feed_ctr.read()[0].dump()
        feed_ctr.delete(feed['id'])
        self.assertFalse(0,
                ArticleController().read(feed_id=feed['id']).count())

    def test_feed_list_fetchable(self):
        self.assertEquals(3, len(FeedController(3).list_fetchable()))
        self.assertEquals(0, len(FeedController(3).list_fetchable()))
        self.assertEquals(3, len(FeedController().list_fetchable()))
        self.assertEquals(0, len(FeedController().list_fetchable()))
        self.assertEquals(3,
                len(FeedController(3).list_fetchable(refresh_rate=0)))
        self.assertEquals(5,
                len(FeedController().list_fetchable(refresh_rate=0)))

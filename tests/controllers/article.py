from tests.base import BasePyaggTest
from pyaggr3g470r.controllers import ArticleController
from pyaggr3g470r.controllers import FeedController


class ArticleControllerTest(BasePyaggTest):
    _contr_cls = ArticleController

    def test_article_rights(self):
        article = ArticleController(2).read()[0].dump()
        self.assertFalse(article['readed'])
        article['readed'] = True  # article get read when retreived through get
        self._test_controller_rights(article, article['user_id'])

    def test_article_challange_method(self):
        self.assertEquals(0, len(list(ArticleController().challenge(
                [{'id': art.id} for art in ArticleController(3).read()]))))
        self.assertEquals(9, len(list(ArticleController(2).challenge(
                [{'id': art.id} for art in ArticleController(3).read()]))))
        self.assertEquals(9, len(list(ArticleController(2).challenge(
                [{'entry_id': art.id} for art in ArticleController(3).read()]
        ))))

    def test_article_get_unread(self):
        self.assertEquals({1: 3, 2: 3, 3: 3},
                ArticleController(2).get_unread())
        self.assertEquals({4: 3, 5: 3, 6: 3},
                ArticleController(3).get_unread())

    def test_create_using_filters(self):
        feed_ctr = FeedController(2)
        feed1 = feed_ctr.read()[0].dump()
        feed2 = feed_ctr.read()[1].dump()
        feed3 = feed_ctr.read()[2].dump()
        feed_ctr.update({'id': feed1['id']},
                        {'filters': [{"type": "simple match",
                                      "pattern": "no see pattern",
                                      "action on": "match",
                                      "action": "mark as read"}]})
        feed_ctr.update({'id': feed3['id']},
                        {'filters': [{"type": "regex",
                                      "pattern": ".*(pattern1|pattern2).*",
                                      "action on": "no match",
                                      "action": "mark as favorite"},
                                     {"type": "simple match",
                                      "pattern": "no see pattern",
                                      "action on": "match",
                                      "action": "mark as read"}]})
        art1 = ArticleController(2).create(
                entry_id="thisisnotatest",
                feed_id=feed1['id'],
                title="garbage no see pattern garbage",
                content="doesn't matter",
                link="doesn't matter either")
        art2 = ArticleController(2).create(
                entry_id="thisisnotatesteither",
                feed_id=feed1['id'],
                title="garbage see pattern garbage",
                content="doesn't matter2",
                link="doesn't matter either2")

        art3 = ArticleController(2).create(
                entry_id="thisisnotatest",
                user_id=2,
                feed_id=feed2['id'],
                title="garbage no see pattern garbage",
                content="doesn't matter",
                link="doesn't matter either")
        art4 = ArticleController(2).create(
                entry_id="thisisnotatesteither",
                user_id=2,
                feed_id=feed2['id'],
                title="garbage see pattern garbage",
                content="doesn't matter2",
                link="doesn't matter either2")

        art5 = ArticleController(2).create(
                entry_id="thisisnotatest",
                feed_id=feed3['id'],
                title="garbage pattern1 garbage",
                content="doesn't matter",
                link="doesn't matter either")
        art6 = ArticleController(2).create(
                entry_id="thisisnotatesteither",
                feed_id=feed3['id'],
                title="garbage pattern2 garbage",
                content="doesn't matter2",
                link="doesn't matter either2")
        art7 = ArticleController(2).create(
                entry_id="thisisnotatesteither",
                feed_id=feed3['id'],
                title="garbage no see pattern3 garbage",
                content="doesn't matter3",
                link="doesn't matter either3")
        art8 = ArticleController(2).create(
                entry_id="thisisnotatesteither",
                feed_id=feed3['id'],
                title="garbage pattern4 garbage",
                content="doesn't matter4",
                link="doesn't matter either4")

        self.assertTrue(art1.readed)
        self.assertFalse(art1.like)
        self.assertFalse(art2.readed)
        self.assertFalse(art2.like)
        self.assertFalse(art3.readed)
        self.assertFalse(art3.like)
        self.assertFalse(art4.readed)
        self.assertFalse(art4.like)
        self.assertFalse(art5.readed)
        self.assertFalse(art5.like)
        self.assertFalse(art6.readed)
        self.assertFalse(art6.like)
        self.assertTrue(art7.readed)
        self.assertTrue(art7.like)
        self.assertFalse(art8.readed)
        self.assertTrue(art8.like)

from datetime import datetime
from flask import Blueprint, g, render_template

from pyaggr3g470r import controllers, utils
from pyaggr3g470r.decorators import pyagg_default_decorator, \
                                    feed_access_required

feeds_bp = Blueprint('feeds', __name__, url_prefix='/feeds')
feed_bp = Blueprint('feed', __name__, url_prefix='/feed')

@feeds_bp.route('/', methods=['GET'])
def feeds():
    "Lists the subscribed  feeds in a table."
    return render_template('feeds.html',
            feeds=controllers.FeedController(g.user.id).read())


@feed_bp.route('/<int:feed_id>', methods=['GET'])
@pyagg_default_decorator
@feed_access_required
def feed(feed_id=None):
    "Presents detailed information about a feed."
    feed = controllers.FeedController(g.user.id).get(id=feed_id)
    word_size = 6
    articles = controllers.ArticleController(g.user.id)\
                          .read(feed_id=feed_id).all()
    nb_articles = controllers.ArticleController(g.user.id).read().count()
    top_words = utils.top_words(articles, n=50, size=int(word_size))
    tag_cloud = utils.tag_cloud(top_words)

    today = datetime.now()
    try:
        last_article = articles[0].date
        first_article = articles[-1].date
        delta = last_article - first_article
        average = round(float(len(articles)) / abs(delta.days), 2)
    except:
        last_article = datetime.fromtimestamp(0)
        first_article = datetime.fromtimestamp(0)
        delta = last_article - first_article
        average = 0
    elapsed = today - last_article

    return render_template('feed.html',
                           head_title=utils.clear_string(feed.title),
                           feed=feed, tag_cloud=tag_cloud,
                           first_post_date=first_article,
                           end_post_date=last_article,
                           nb_articles=nb_articles,
                           average=average, delta=delta, elapsed=elapsed)

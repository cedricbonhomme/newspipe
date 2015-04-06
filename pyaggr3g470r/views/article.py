#! /usr/bin/env python
# -*- coding: utf-8 -

from flask import Blueprint, g, render_template, redirect
from sqlalchemy import desc

from pyaggr3g470r import controllers, utils
from pyaggr3g470r.decorators import pyagg_default_decorator

articles_bp = Blueprint('articles', __name__, url_prefix='/articles')
article_bp = Blueprint('article', __name__, url_prefix='/article')


@articles_bp.route('/<feed_id>', methods=['GET'])
@articles_bp.route('/<feed_id>/<int:nb_articles>', methods=['GET'])
@pyagg_default_decorator
def articles(feed_id=None, nb_articles=-1):
    """List articles of a feed. The administrator of the platform is able to
    access to this view for every users."""
    feed = controllers.FeedController(g.user.id).get(id=feed_id)
    feed.articles = controllers.ArticleController(g.user.id)\
                               .read(feed_id=feed.id)\
                               .order_by(desc("Article.date"))
    if len(feed.articles.all()) <= nb_articles or nb_articles == -1:
        nb_articles = int(1e9)
    feed.articles = feed.articles.limit(nb_articles)
    return render_template('articles.html', feed=feed, nb_articles=nb_articles)


@article_bp.route('/redirect/<int:article_id>', methods=['GET'])
@pyagg_default_decorator
def redirect_to_article(article_id):
    article = controllers.ArticleController(g.user.id).get(id=article_id)
    return redirect(article.link)


@article_bp.route('/<int:article_id>', methods=['GET'])
@pyagg_default_decorator
def article(article_id=None):
    """
    Presents the content of an article.
    """
    article = controllers.ArticleController(g.user.id).get(id=article_id)
    previous_article = article.previous_article()
    if previous_article is None:
        previous_article = article.source.articles[0]
    next_article = article.next_article()
    if next_article is None:
        next_article = article.source.articles[-1]

    return render_template('article.html',
                           head_title=utils.clear_string(article.title),
                           article=article,
                           previous_article=previous_article,
                           next_article=next_article)

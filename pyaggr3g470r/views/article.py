#! /usr/bin/env python
# -*- coding: utf-8 -

from flask import Blueprint, g, render_template, redirect

from pyaggr3g470r import controllers, utils
from pyaggr3g470r.decorators import pyagg_default_decorator

articles_bp = Blueprint('articles', __name__, url_prefix='/articles')
article_bp = Blueprint('article', __name__, url_prefix='/article')


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
                           head_titles=[utils.clear_string(article.title)],
                           article=article,
                           previous_article=previous_article,
                           next_article=next_article)

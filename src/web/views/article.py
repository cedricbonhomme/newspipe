#! /usr/bin/env python
# -*- coding: utf-8 -
from datetime import datetime, timedelta
from flask import (Blueprint, g, render_template, redirect,
                   flash, url_for, request)
from flask.ext.babel import gettext
from flask.ext.login import login_required

from web.lib.utils import clear_string, redirect_url
from web.controllers import ArticleController
from web.lib.view_utils import etag_match

articles_bp = Blueprint('articles', __name__, url_prefix='/articles')
article_bp = Blueprint('article', __name__, url_prefix='/article')


@article_bp.route('/redirect/<int:article_id>', methods=['GET'])
@login_required
def redirect_to_article(article_id):
    article = ArticleController(g.user.id).get(id=article_id)
    return redirect(article.link)


@article_bp.route('/<int:article_id>', methods=['GET'])
@login_required
@etag_match
def article(article_id=None):
    """
    Presents the content of an article.
    """
    article = ArticleController(g.user.id).get(id=article_id)
    previous_article = article.previous_article()
    if previous_article is None:
        previous_article = article.source.articles[0]
    next_article = article.next_article()
    if next_article is None:
        next_article = article.source.articles[-1]

    return render_template('article.html',
                           head_titles=[clear_string(article.title)],
                           article=article,
                           previous_article=previous_article,
                           next_article=next_article)


@article_bp.route('/like/<int:article_id>', methods=['GET'])
@login_required
def like(article_id=None):
    """
    Mark or unmark an article as favorites.
    """
    art_contr = ArticleController(g.user.id)
    article = art_contr.get(id=article_id)
    art_contr = art_contr.update({'id': article_id},
                                 {'like': not article.like})
    return redirect(redirect_url())


@article_bp.route('/delete/<int:article_id>', methods=['GET'])
@login_required
def delete(article_id=None):
    """
    Delete an article from the database.
    """
    article = ArticleController(g.user.id).delete(article_id)
    flash(gettext('Article %(article_title)s deleted',
                  article_title=article.title), 'success')
    return redirect(url_for('home'))


@articles_bp.route('/history', methods=['GET'])
@articles_bp.route('/history/<int:year>', methods=['GET'])
@articles_bp.route('/history/<int:year>/<int:month>', methods=['GET'])
@login_required
def history(year=None, month=None):
    counter, articles = ArticleController(g.user.id).get_history(year, month)
    return render_template('history.html', articles_counter=counter,
                           articles=articles, year=year, month=month)


@article_bp.route('/mark_as/<string:new_value>', methods=['GET'])
@article_bp.route('/mark_as/<string:new_value>/article/<int:article_id>',
                  methods=['GET'])
@login_required
def mark_as(new_value='read', feed_id=None, article_id=None):
    """
    Mark all unreaded articles as read.
    """
    readed = new_value == 'read'
    art_contr = ArticleController(g.user.id)
    filters = {'readed': not readed}
    if feed_id is not None:
        filters['feed_id'] = feed_id
        message = 'Feed marked as %s.'
    elif article_id is not None:
        filters['id'] = article_id
        message = 'Article marked as %s.'
    else:
        message = 'All article marked as %s.'
    art_contr.update(filters, {"readed": readed})
    flash(gettext(message % new_value), 'info')

    if readed:
        return redirect(redirect_url())
    return redirect('home')


@articles_bp.route('/expire_articles', methods=['GET'])
@login_required
def expire():
    """
    Delete articles older than the given number of weeks.
    """
    current_time = datetime.utcnow()
    weeks_ago = current_time - timedelta(int(request.args.get('weeks', 10)))
    art_contr = ArticleController(g.user.id)

    query = art_contr.read(__or__={'date__lt': weeks_ago,
                                   'retrieved_date__lt': weeks_ago})
    count = query.count()
    query.delete()
    flash(gettext('%(count)d articles deleted', count=count), 'info')
    return redirect(redirect_url())

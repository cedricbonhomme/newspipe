from datetime import datetime, timedelta
from flask import (Blueprint, g, render_template, redirect,
                   flash, url_for, make_response, request)

from flask_babel import gettext
from flask_login import login_required, current_user


from bootstrap import db
from web.export import export_json, export_html
from web.lib.utils import clear_string, redirect_url
from web.controllers import (ArticleController, UserController,
                            CategoryController)
from web.lib.view_utils import etag_match

articles_bp = Blueprint('articles', __name__, url_prefix='/articles')
article_bp = Blueprint('article', __name__, url_prefix='/article')


@article_bp.route('/redirect/<int:article_id>', methods=['GET'])
@login_required
def redirect_to_article(article_id):
    contr = ArticleController(current_user.id)
    article = contr.get(id=article_id)
    if not article.readed:
        contr.update({'id': article.id}, {'readed': True})
    return redirect(article.link)


@article_bp.route('/<int:article_id>', methods=['GET'])
@login_required
@etag_match
def article(article_id=None):
    """
    Presents the content of an article.
    """
    article = ArticleController(current_user.id).get(id=article_id)
    return render_template('article.html',
                           head_titles=[clear_string(article.title)],
                           article=article)


@article_bp.route('/like/<int:article_id>', methods=['GET'])
@login_required
def like(article_id=None):
    """
    Mark or unmark an article as favorites.
    """
    art_contr = ArticleController(current_user.id)
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
    article = ArticleController(current_user.id).delete(article_id)
    flash(gettext('Article %(article_title)s deleted',
                  article_title=article.title), 'success')
    return redirect(url_for('home'))


@articles_bp.route('/history', methods=['GET'])
@articles_bp.route('/history/<int:year>', methods=['GET'])
@articles_bp.route('/history/<int:year>/<int:month>', methods=['GET'])
@login_required
def history(year=None, month=None):
    cntr, artcles = ArticleController(current_user.id).get_history(year, month)
    return render_template('history.html', articles_counter=cntr,
                           articles=artcles, year=year, month=month)


@article_bp.route('/mark_as/<string:new_value>', methods=['GET'])
@article_bp.route('/mark_as/<string:new_value>/article/<int:article_id>',
                  methods=['GET'])
@login_required
def mark_as(new_value='read', feed_id=None, article_id=None):
    """
    Mark all unreaded articles as read.
    """
    readed = new_value == 'read'
    art_contr = ArticleController(current_user.id)
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
    art_contr = ArticleController(current_user.id)

    query = art_contr.read(__or__={'date__lt': weeks_ago,
                                   'retrieved_date__lt': weeks_ago})
    count = query.count()
    query.delete()
    db.session.commit()
    flash(gettext('%(count)d articles deleted', count=count), 'info')
    return redirect(redirect_url())


@articles_bp.route('/export', methods=['GET'])
@login_required
def export():
    """
    Export all articles to HTML or JSON.
    """
    user = UserController(current_user.id).get(id=current_user.id)
    if request.args.get('format') == "HTML":
        # Export to HTML
        try:
            archive_file, archive_file_name = export_html(user)
        except Exception as e:
            print(e)
            flash(gettext("Error when exporting articles."), 'danger')
            return redirect(redirect_url())
        response = make_response(archive_file)
        response.headers['Content-Type'] = 'application/x-compressed'
        response.headers['Content-Disposition'] = 'attachment; filename=%s' \
                % archive_file_name
    elif request.args.get('format') == "JSON":
        # Export to JSON
        try:
            json_result = export_json(user)
        except Exception as e:
            flash(gettext("Error when exporting articles."), 'danger')
            return redirect(redirect_url())
        response = make_response(json_result)
        response.mimetype = 'application/json'
        response.headers["Content-Disposition"] \
                = 'attachment; filename=account.json'
    elif request.args.get('format') == "OPML":
        categories = {cat.id: cat.dump()
                for cat in CategoryController(user.id).read()}
        response = make_response(render_template('opml.xml', user=user,
                                                categories=categories,
                                                now=datetime.now()))
        response.headers['Content-Type'] = 'application/xml'
        response.headers['Content-Disposition'] = 'attachment; filename=feeds.opml'
    else:
        flash(gettext('Export format not supported.'), 'warning')
        return redirect(redirect_url())
    return response

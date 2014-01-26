#! /usr/bin/env python
# -*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2013  Cédric Bonhomme - http://cedricbonhomme.org/
#
# For more information : http://bitbucket.org/cedricbonhomme/pyaggr3g470r/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 4.4 $"
__date__ = "$Date: 2010/01/29 $"
__revision__ = "$Date: 2013/12/27 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

import datetime
from flask import render_template, request, make_response, flash, session, url_for, redirect, g
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user, AnonymousUserMixin

import conf
import utils
import export
import feedgetter
import models
import search as fastsearch
from forms import SigninForm, AddFeedForm, ProfileForm
from pyaggr3g470r import app, db

login_manager = LoginManager()
login_manager.init_app(app)

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        pass
        #g.user.last_seen = datetime.utcnow()
        #db.session.add(g.user)
        #db.session.commit()

@app.errorhandler(403)
def authentication_failed(e):
    flash('Authentication failed.', 'danger')
    return redirect(url_for('login'))

@app.errorhandler(401)
def authentication_failed(e):
    flash('Authentication required.', 'info')
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(email):
    # Return an instance of the User model
    return models.User.objects(email=email).first()

@app.route('/login/', methods=['GET', 'POST'])
def login():
    g.user = AnonymousUserMixin()
    form = SigninForm()

    if form.validate_on_submit():
        user = models.User.objects(email=form.email.data).first()
        login_user(user)
        g.user = user
        flash("Logged in successfully.", 'success')
        return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/logout/')
@login_required
def logout():
    """
    Remove the user information from the session.
    """
    logout_user()
    flash("Logged out successfully.", 'success')
    return redirect(url_for('home'))





@app.route('/')
@login_required
def home():
    """
    The home page lists most recent articles of all feeds.
    """
    user = g.user
    feeds = models.User.objects(email=g.user.email).fields(slice__feeds__articles=9).first().feeds
    return render_template('home.html', user=user, feeds=feeds, \
                            head_title=models.Article.objects(readed=False).count())

@app.route('/fetch/', methods=['GET'])
@app.route('/fetch/<feed_id>', methods=['GET'])
@login_required
def fetch(feed_id=None):
    """
    Triggers the download of news.
    """
    feed_getter = feedgetter.FeedGetter(g.user.email)
    feed_getter.retrieve_feed(feed_id)
    flash("New articles retrieved.", 'success')
    return redirect(url_for('home'))

@app.route('/about/', methods=['GET'])
@login_required
def about():
    """
    'About' page.
    """
    return render_template('about.html')

@app.route('/feeds/', methods=['GET'])
@login_required
def feeds():
    """
    Lists the subscribed  feeds in a table.
    """
    feeds = models.User.objects(email=g.user.email).first().feeds
    return render_template('feeds.html', feeds=feeds)

@app.route('/feed/<feed_id>', methods=['GET'])
@login_required
def feed(feed_id=None):
    """
    Presents detailed information about a feed.
    """
    word_size = 6
    user = models.User.objects(email=g.user.email, feeds__oid=feed_id).first()
    for feed in user.feeds:
        if str(feed.oid) == feed_id:
            articles = feed.articles
            top_words = utils.top_words(articles, n=50, size=int(word_size))
            tag_cloud = utils.tag_cloud(top_words)

            today = datetime.datetime.now()
            try:
                last_article = articles[0].date
                first_article = articles[-1].date
                delta = last_article - first_article
                average = round(float(len(articles)) / abs(delta.days), 2)
            except:
                last_article = datetime.datetime.fromtimestamp(0)
                first_article = datetime.datetime.fromtimestamp(0)
                delta = last_article - first_article
                average = 0
            elapsed = today - last_article

            return render_template('feed.html', head_title=feed.title, feed=feed, tag_cloud=tag_cloud, \
                                   first_post_date=first_article, end_post_date=last_article , \
                                   average=average, delta=delta, elapsed=elapsed)

@app.route('/article/<article_id>', methods=['GET'])
@login_required
def article(article_id=None):
    """
    Presents the content of an article.
    """
    #user = models.User.objects(email=g.user.email, feeds__oid=feed_id).first()
    article = models.Article.objects(id=article_id).first()
    if not article.readed:
        article.readed = True
        article.save()
    return render_template('article.html', head_title=article.title, article=article)

@app.route('/mark_as_read/', methods=['GET'])
@login_required
def mark_as_read():
    """
    Mark all unreaded articles as read.
    """
    #user = models.User.objects(email=g.user.email).first()
    models.Article.objects(readed=False).update(set__readed=True)
    return redirect(url_for('home'))

@app.route('/like/<article_id>', methods=['GET'])
@login_required
def like(article_id=None):
    """
    Mark or unmark an article as favorites.
    """
    #user = models.User.objects(email=g.user.email).first()
    models.Article.objects(id=article_id).update(set__like= \
                                        (not models.Article.objects(id=article_id).first().like))
    return redirect("/article/"+article_id)

@app.route('/delete/<article_id>', methods=['GET'])
@login_required
def delete(article_id=None):
    """
    Delete an article from the MongoDB and the Whoosh
    databases.
    """
    user = models.User.objects(email=g.user.email).first()
    # delete the article
    for feed in user.feeds:
        for article in feed.articles:
            if str(article.id) == article_id:
                feed.articles.remove(article)
                article.delete()
                user.save()
                try:
                    fastsearch.delete_article(str(feed.oid), str(article.id))
                except:
                    # if index is empty
                    pass
                flash('Article "' + article.title + '" deleted.', 'success')
                return redirect(url_for('home'))
    flash('Impossible to delete the article.', 'danger')
    return redirect(url_for('home'))

@app.route('/articles/<feed_id>', methods=['GET'])
@login_required
def articles(feed_id=None):
    user = models.User.objects(email=g.user.email, feeds__oid=feed_id).first()
    for feed in user.feeds:
        if str(feed.oid) == feed_id:
            return render_template('articles.html', feed=feed)

@app.route('/favorites/', methods=['GET'])
@login_required
def favorites():
    """
    List favorites articles.
    """
    user = models.User.objects(email=g.user.email).first()
    result = []
    for feed in user.feeds:
        feed.articles = [article for article in feed.articles if article.like]
        if len(feed.articles) != 0:
            result.append(feed)
    return render_template('favorites.html', feeds=result)

@app.route('/unread/', methods=['GET'])
@login_required
def unread():
    """
    List unread articles.
    """
    user = models.User.objects(email=g.user.email).first()
    result = []
    for feed in user.feeds:
        feed.articles = [article for article in feed.articles if not article.readed]
        if len(feed.articles) != 0:
            result.append(feed)
    return render_template('unread.html', feeds=result)

@app.route('/inactives/', methods=['GET'])
@login_required
def inactives():
    """
    List of inactive feeds.
    """
    nb_days = int(request.args.get('nb_days', 365))
    user = models.User.objects(email=g.user.email).first()
    today = datetime.datetime.now()
    inactives = []
    for feed in user.feeds:
        last_post = feed.articles[0].date
        elapsed = today - last_post
        if elapsed > datetime.timedelta(days=nb_days):
            inactives.append((feed, elapsed))
    return render_template('inactives.html', inactives=inactives, nb_days=nb_days)

@app.route('/index_database/', methods=['GET'])
@login_required
def index_database():
    """
    Index all the database.
    """
    user = models.User.objects(email=g.user.email).first()
    fastsearch.create_index(user.feeds)
    return redirect(url_for('home'))

@app.route('/export/', methods=['GET'])
@login_required
def export_articles():
    """
    Export all articles.
    """
    user = models.User.objects(email=g.user.email).first()
    try:
        archive_file, archive_file_name = export.export_html(user.feeds)
    except:
        flash("Error when exporting articles.", 'danger')
        return redirect(url_for('management'))
    response = make_response(archive_file)
    response.headers['Content-Type'] = 'application/x-compressed'
    response.headers['Content-Disposition'] = 'attachment; filename='+archive_file_name
    return response

@app.route('/search/', methods=['GET'])
@login_required
def search():
    """
    Search articles corresponding to the query.
    """
    user = models.User.objects(email=g.user.email).first()
    result = []
    query = request.args.get('query', None)
    if query != None:
        results, nb_articles = fastsearch.search(query)
        for feed_id in results:
            for feed in user.feeds:
                if str(feed.oid) == feed_id:
                    feed.articles = []
                    for article_id in results[feed_id]:
                        current_article = models.Article.objects(id=article_id).first()
                        feed.articles.append(current_article)
                    feed.articles = sorted(feed.articles, key=lambda t: t.date, reverse=True)
                    result.append(feed)
    return render_template('search.html', feeds=result, nb_articles=nb_articles, query=query)

@app.route('/management/', methods=['GET'])
@login_required
def management():
    """
    Display the management page.
    """
    form = AddFeedForm()
    user = models.User.objects(email=g.user.email).first()
    nb_feeds = len(user.feeds)
    #nb_articles = sum([len(feed.articles) for feed in user.feeds])
    #nb_unread_articles = sum([len([article for article in feed.articles if not article.readed]) for feed in user.feeds])
    nb_articles = models.Article.objects().count()
    nb_unread_articles = models.Article.objects(readed=False).count()
    return render_template('management.html', form=form, \
                            nb_feeds=nb_feeds, nb_articles=nb_articles, nb_unread_articles=nb_unread_articles)

@app.route('/history/', methods=['GET'])
@login_required
def history():
    user = models.User.objects(email=g.user.email).first()
    return render_template('history.html')

@app.route('/edit_feed/', methods=['GET', 'POST'])
@app.route('/edit_feed/<feed_id>', methods=['GET', 'POST'])
@login_required
def edit_feed(feed_id=None):
    """
    Add or edit a feed.
    """
    user = models.User.objects(email=g.user.email).first()
    form = AddFeedForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('edit_feed.html', form=form)
        if feed_id != None:
            # Edit an existing feed
            for feed in user.feeds:
                if str(feed.oid) == feed_id:
                    form.populate_obj(feed)
                    user.save()
                    flash('Feed "' + feed.title + '" successfully updated.', 'success')
                    return redirect('/edit_feed/' + feed_id)
        else:
            # Create a new feed
            existing_feed = [feed for feed in user.feeds if feed.link == form.link.data]
            if len(existing_feed) == 0:
                new_feed = models.Feed(title=form.title.data, description="", link=form.link.data, \
                                        site_link=form.site_link.data, email=form.email_notification.data, \
                                        enabled=form.enabled.data)
                user.feeds.append(new_feed)
                user.feeds = sorted(user.feeds, key=lambda t: t.title.lower())
                user.save()
                flash('Feed "' + new_feed.title + '" successfully created.', 'success')
                return redirect('/edit_feed/' + str(new_feed.oid))
            else:
                flash('Feed "' + existing_feed[0].title + '" already in the database.', 'warning')
                return redirect('/edit_feed/' + str(existing_feed[0].oid))

    if request.method == 'GET':
        if feed_id != None:
            for feed in user.feeds:
                if str(feed.oid) == feed_id:
                    form = AddFeedForm(obj=feed)
                    return render_template('edit_feed.html', action="Edit the feed", form=form, feed=feed)

        # Return an empty form in order to create a new feed
        return render_template('edit_feed.html', action="Add a feed", form=form)

@app.route('/delete_feed/<feed_id>', methods=['GET'])
@login_required
def delete_feed(feed_id=None):
    """
    Delete a feed with all associated articles.
    """
    user = models.User.objects(email=g.user.email).first()
    # delete all articles (Document objects) of the feed
    for feed in user.feeds:
        if str(feed.oid) == feed_id:
            for article in feed.articles:
                article.delete()
            feed.articles = []
            # delete the feed (EmbeddedDocument object)
            user.feeds.remove(feed)
            user.save()
            flash('Feed "' + feed.title + '" successfully deleted.', 'success')
            break
    else:
        flash('Impossible to delete this feed.', 'danger')
    return redirect(url_for('home'))

@app.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Edit the profile of the user.
    """
    user = models.User.objects(email=g.user.email).first()
    form = ProfileForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('profile.html', form=form)

        form.populate_obj(user)
        if form.password.data != "":
            user.set_password(form.password.data)
        user.save()
        flash('User "' + user.firstname + '" successfully updated', 'success')
        return redirect('/profile/')

    if request.method == 'GET':
        form = ProfileForm(obj=user)
        return render_template('profile.html', form=form)

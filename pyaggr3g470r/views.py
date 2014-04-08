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
__version__ = "$Revision: 4.5 $"
__date__ = "$Date: 2010/01/29 $"
__revision__ = "$Date: 2014/02/09 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

import os
from datetime import datetime
from flask import render_template, jsonify, request, flash, session, url_for, redirect, g, current_app, make_response
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user, AnonymousUserMixin
from flask.ext.principal import Principal, Identity, AnonymousIdentity, identity_changed, identity_loaded, Permission, RoleNeed, UserNeed

import conf
import utils
import export
import feedgetter
import models
import search as fastsearch
from forms import SigninForm, AddFeedForm, ProfileForm
from pyaggr3g470r import app, db
from pyaggr3g470r.models import User, Feed, Article, Role

login_manager = LoginManager()
login_manager.init_app(app)

#
# Management of the user's session.
#
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))

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
    return User.query.filter(User.email == email).first()

def redirect_url(default='index'):
    return request.args.get('next') or \
            request.referrer or \
            url_for(default)



from functools import wraps
def feed_access_required(func):
    """
    This decorator enables to check if a user has access to a feed.
    """
    #print("Now decorating %s" % func)
    @wraps(func)
    def decorated(*args, **kwargs):
        #print("Now calling %s with %s,%s" % (func, args, kwargs))
        if kwargs.get('feed_id', None) != None:
            feed = Feed.query.filter(Feed.id == kwargs.get('feed_id', None)).first()
            if feed == None or feed.subscriber.id != g.user.id:
                flash("This feed do not exist.", "danger")
                return redirect(url_for('home'))
        return func(*args, **kwargs)
    return decorated





#
# Views.
#
@app.route('/login/', methods=['GET', 'POST'])
def login():
    """
    Log in view.
    """
    g.user = AnonymousUserMixin()
    form = SigninForm()

    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()
        login_user(user)
        g.user = user
        identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
        flash("Logged in successfully.", 'success')
        return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/logout/')
@login_required
def logout():
    """
    Log out view. Removes the user information from the session.
    """
    # Update last_seen field
    g.user.last_seen = datetime.utcnow()
    db.session.add(g.user)
    db.session.commit()

    # Remove the user information from the session
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())

    flash("Logged out successfully.", 'success')
    return redirect(url_for('map_view'))

@app.route('/')
@login_required
def home():
    """
    The home page lists most recent articles of all feeds.
    """
    user = User.query.filter(User.email == g.user.email).first()
    return render_template('home.html', user=user, head_title="nb unread")

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
    return redirect(redirect_url())

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
    user = User.query.filter(User.email == g.user.email).first()
    feeds = user.feeds
    return render_template('feeds.html', feeds=feeds)

@app.route('/feed/<int:feed_id>', methods=['GET'])
@login_required
def feed(feed_id=None):
    """
    Presents detailed information about a feed.
    """
    feed = Feed.query.filter(Feed.id == feed_id).first()
    if feed.subscriber.id == g.user.id:
        word_size = 6
        articles = feed.articles
        nb_articles = len(feed.articles.all())
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

        return render_template('feed.html', head_title=utils.clear_string(feed.title), feed=feed, tag_cloud=tag_cloud, \
                            first_post_date=first_article, end_post_date=last_article , nb_articles=nb_articles, \
                            average=average, delta=delta, elapsed=elapsed)
    else:
        flash("This feed do not exist.", 'warning')
        return redirect(redirect_url())

@app.route('/article/<int:article_id>', methods=['GET'])
@login_required
def article(article_id=None):
    """
    Presents the content of an article.
    """
    article = Article.query.filter(Article.id == article_id).first()
    if article.source.subscriber.id == g.user.id:
        if article == None:
            flash("This article do not exist.", 'warning')
            return redirect(redirect_url())
        if not article.readed:
            article.readed = True
            db.session.commit()
    return render_template('article.html', head_title=utils.clear_string(article.title), article=article)

@app.route('/mark_as_read/', methods=['GET'])
@app.route('/mark_as_read/<int:feed_id>', methods=['GET'])
@login_required
@feed_access_required
def mark_as_read(feed_id=None):
    """
    Mark all unreaded articles as read.
    """
    if feed_id != None:
        Article.query.filter(Article.readed == False).join(Feed).filter(Feed.id == feed_id).update({"readed": True})
        flash('Articles marked as read.', 'info')
    else:
        Article.query.filter(Article.readed == False).update({"readed": True})
        flash("All articles marked as read", 'info')
    db.session.commit()
    return redirect(redirect_url())

@app.route('/like/<int:article_id>', methods=['GET'])
@login_required
def like(article_id=None):
    """
    Mark or unmark an article as favorites.
    """
    #user = models.User.objects(email=g.user.email).first()
    Article.query.filter(Article.id == article_id). \
                update({
                        "like": not Article.query.filter(Article.id == article_id).first().like
                       })
    db.session.commit()
    return redirect(redirect_url())

@app.route('/delete/<int:article_id>', methods=['GET'])
@login_required
def delete(article_id=None):
    """
    Delete an article from the database.
    """
    article = Article.query.filter(Article.id == article_id).first()
    if article != None:
        db.session.delete(article)
        db.session.commit()
        flash('Article "' + article.title + '" deleted.', 'success')
        return redirect(url_for('home'))
    else:
        flash('Impossible to delete the article.', 'danger')
        return redirect(url_for('home'))

@app.route('/articles/<feed_id>/', methods=['GET'])
@app.route('/articles/<feed_id>/<int:nb_articles>', methods=['GET'])
@login_required
def articles(feed_id=None, nb_articles=-1):
    feed = Feed.query.filter(Feed.id == feed_id).first()
    if feed == None:
        flash("No such feed.", "danger")
        return redirect(url_for('home'))
    else:
        if len(feed.articles.all()) <= nb_articles:
            nb_articles = -1
        if nb_articles != -1:
            feed.articles = feed.articles[0:nb_articles]
        return render_template('articles.html', feed=feed, nb_articles=nb_articles)

@app.route('/favorites/', methods=['GET'])
@login_required
def favorites():
    """
    List favorites articles.
    """
    user = models.User.objects(email=g.user.email).first()
    result = []
    nb_favorites = 0
    for feed in user.feeds:
        feed.articles = [article for article in feed.articles if article.like]
        length = len(feed.articles)
        if length != 0:
            result.append(feed)
            nb_favorites += length
    return render_template('favorites.html', feeds=result, nb_favorites=nb_favorites)

@app.route('/unread/', methods=['GET'])
@login_required
def unread():
    """
    List unread articles.
    """
    user = models.User.objects(email=g.user.email).first()
    result = []
    nb_unread = 0
    for feed in user.feeds:
        feed.articles = [article for article in feed.articles if not article.readed]
        length = len(feed.articles)
        if length != 0:
            result.append(feed)
            nb_unread += length
    return render_template('unread.html', feeds=result, nb_unread=nb_unread)

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
        try:
            last_post = feed.articles[0].date
        except IndexError:
            continue
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
    flash('Database indexed.', 'success')
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

@app.route('/export_opml/', methods=['GET'])
@login_required
def export_opml():
    """
    Export all feeds to OPML.
    """
    user = models.User.objects(email=g.user.email).first()
    response = make_response(render_template('opml.xml', user=user, now=datetime.datetime.now()))
    response.headers['Content-Type'] = 'application/xml'
    response.headers['Content-Disposition'] = 'attachment; filename=feeds.opml'
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

@app.route('/management/', methods=['GET', 'POST'])
@login_required
def management():
    """
    Display the management page.
    """
    if request.method == 'POST':
        # Import an OPML file
        data = request.files['opmlfile']
        opml_path = os.path.join("./pyaggr3g470r/var/", data.filename)
        data.save(opml_path)
        try:
            nb = utils.import_opml(g.user.email, opml_path)
            flash(str(nb) + " feeds imported.", "success")
        except Exception as e:
            flash("Impossible to import the new feeds.", "danger")


    form = AddFeedForm()
    user = User.query.filter(User.id == g.user.id).first()
    nb_feeds = len(user.feeds.all())
    #nb_articles = sum([len(feed.articles) for feed in user.feeds])
    #nb_unread_articles = sum([len([article for article in feed.articles if not article.readed]) for feed in user.feeds])
    #articles = Article.query.filter(Article.feed.subscriber.id == g.user.id).all()
    nb_articles = sum([len(feed.articles.all()) for feed in user.feeds])
    nb_unread_articles = 2
    return render_template('management.html', form=form, \
                            nb_feeds=nb_feeds, nb_articles=nb_articles, nb_unread_articles=nb_unread_articles)

@app.route('/history/', methods=['GET'])
@login_required
def history():
    user = models.User.objects(email=g.user.email).first()
    return render_template('history.html')

@app.route('/create_feed/', methods=['GET', 'POST'])
@app.route('/edit_feed/<int:feed_id>', methods=['GET', 'POST'])
@login_required
@feed_access_required
def edit_feed(feed_id=None):
    """
    Add or edit a feed.
    """
    feed = Feed.query.filter(Feed.id == feed_id).first()
    form = AddFeedForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('edit_feed.html', form=form)
        if feed_id != None:
            # Edit an existing feed
            form.populate_obj(feed)
            db.session.commit()
            flash('Feed "' + feed.title + '" successfully updated.', 'success')
            return redirect('/edit_feed/' + str(feed_id))
        else:
            # Create a new feed
            existing_feed = [feed for feed in g.user.feeds if feed.link == form.link.data]
            if len(existing_feed) == 0:
                new_feed = Feed(title=form.title.data, description="", link=form.link.data, \
                                site_link=form.site_link.data, email_notification=form.email_notification.data, \
                                enabled=form.enabled.data)
                g.user.feeds.append(new_feed)
                #user.feeds = sorted(user.feeds, key=lambda t: t.title.lower())
                db.session.commit()
                flash('Feed "' + new_feed.title + '" successfully created.', 'success')
                return redirect('/edit_feed/' + str(new_feed.id))
            else:
                flash('Feed "' + existing_feed[0].title + '" already in the database.', 'warning')
                return redirect('/edit_feed/' + str(existing_feed[0].id))

    if request.method == 'GET':
        if feed_id != None:
            form = AddFeedForm(obj=feed)
            return render_template('edit_feed.html', action="Edit the feed", form=form, feed=feed)

        # Return an empty form in order to create a new feed
        return render_template('edit_feed.html', action="Add a feed", form=form)

@app.route('/delete_feed/<feed_id>', methods=['GET'])
@login_required
@feed_access_required
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
    return redirect(redirect_url())

@app.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Edit the profile of the currently logged user.
    """
    user = User.query.filter(User.email == g.user.email).first()
    form = ProfileForm()

    if request.method == 'POST':
        if form.validate():
            form.populate_obj(user)
            if form.password.data != "":
                user.set_password(form.password.data)
            db.session.commit()
            flash('User "' + user.firstname + '" successfully updated.', 'success')
            return redirect(url_for('profile'))
        else:
            return render_template('profile.html', form=form)

    if request.method == 'GET':
        form = ProfileForm(obj=user)
        return render_template('profile.html', user=user, form=form)

#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, request, flash, session, url_for, redirect, g
from wtforms import TextField, PasswordField, SubmitField, validators
from flask.ext.mail import Message, Mail
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user, AnonymousUserMixin

from collections import defaultdict

from forms import SigninForm
from pyaggr3g470r import app, db


import feedgetter
import models

mail = Mail()

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
    flash('Authenticated failed.')
    return redirect(url_for('login'))

@app.errorhandler(401)
def authentication_failed(e):
    flash('Authenticated required.')
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
        flash("Logged in successfully.")
        return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/logout/')
@login_required
def logout():
    """
    Remove the user information from the session.
    """
    logout_user()
    return redirect(url_for('home'))





@app.route('/')
@login_required
def home():
    #feeds = models.Feed.objects().order_by('title').fields(slice__articles=[0,9])
    user = g.user
    feeds = models.Feed.objects().fields(slice__articles=9)
    return render_template('home.html', user=user, feeds=feeds)

@app.route('/fetch/', methods=['GET'])
@login_required
def fetch():
    feed_getter = feedgetter.FeedGetter()
    feed_getter.retrieve_feed()
    return redirect(url_for('home'))

@app.route('/about/', methods=['GET'])
@login_required
def about():
    return render_template('about.html')

@app.route('/feeds/', methods=['GET'])
@login_required
def feeds():
    feeds = models.Feed.objects()
    return render_template('feeds.html', feeds=feeds)

@app.route('/feed/<feed_id>', methods=['GET'])
@login_required
def feed(feed_id=None):
    feed = models.Article.objects(id=feed_id).first()
    return render_template('feed.html', feed=feed)

@app.route('/article/<article_id>', methods=['GET'])
@login_required
def article(article_id=None):
    article = models.Article.objects(id=article_id).first()
    if not article.readed:
        article.readed = True
        article.save()
    return render_template('article.html', article=article)

@app.route('/delete/<article_id>', methods=['GET'])
@login_required
def delete(article_id=None):
    article = models.Article.objects(id=article_id).first()
    article.delete()
    article.save()
    return redirect(url_for('home'))

@app.route('/articles/<feed_id>', methods=['GET'])
@login_required
def articles(feed_id=None):
    feed = models.Feed.objects(id=feed_id).first()
    #feed.articles = sorted(feed.articles, key=lambda t: t.date, reverse=True)
    return render_template('articles.html', feed=feed)

@app.route('/favorites/', methods=['GET'])
@login_required
def favorites():
    favorites = defaultdict(list)
    for feed in models.Feed.objects():
        for article in feed.articles:
            if article.like:
                favorites[feed.title].append(article)

    return render_template('favorites.html', favorites=favorites)

@app.route('/unread/', methods=['GET'])
@login_required
def unread():
    feeds = models.Feed.objects().filter(articles__readed=False)
    unread_articles = models.Article.objects.filter(readed = False)
    print len(feeds)
    return render_template('unread.html', feeds=feeds)

@app.route('/management/', methods=['GET'])
@login_required
def management():
    nb_article = models.Article.objects().count()
    return render_template('management.html', nb_article=nb_article)
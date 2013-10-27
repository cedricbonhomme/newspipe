#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, request, flash, session, url_for, redirect
from wtforms import TextField, PasswordField, SubmitField, validators
from flask.ext.mail import Message, Mail

from collections import defaultdict

#from forms import ContactForm, SignupForm, SigninForm
from pyaggr3g470r import app, db

import feedgetter
import models

mail = Mail()

@app.route('/')
def home():
    #feeds = models.Feed.objects().order_by('title').fields(slice__articles=[0,9])
    feeds = models.Feed.objects().fields(slice__articles=[0,9])
    return render_template('home.html', feeds=feeds)

@app.route('/fetch/', methods=['GET'])
def fetch():
    feed_getter = feedgetter.FeedGetter()
    feed_getter.retrieve_feed()
    return redirect(url_for('home'))

@app.route('/about/', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/feeds/', methods=['GET'])
def feeds():
    feeds = models.Feed.objects()
    return render_template('feeds.html', feeds=feeds)

@app.route('/feed/<feed_id>', methods=['GET'])
def feed(feed_id=None):
    feed = models.Article.objects(id=feed_id).first()
    return render_template('feed.html', feed=feed)

@app.route('/article/<article_id>', methods=['GET'])
def article(article_id=None):
    article = models.Article.objects(id=article_id).first()
    if not article.readed:
        article.readed = True
        article.save()
    return render_template('article.html', article=article)

@app.route('/delete/<article_id>', methods=['GET'])
def delete(article_id=None):
    article = models.Article.objects(id=article_id).first()
    article.delete()
    article.save()
    return redirect(url_for('home'))

@app.route('/articles/<feed_id>', methods=['GET'])
def articles(feed_id=None):
    feed = models.Feed.objects(id=feed_id).first()
    feed.articles = sorted(feed.articles, key=lambda t: t.date, reverse=True)
    feed.save()
    return render_template('articles.html', feed=feed)

@app.route('/favorites/', methods=['GET'])
def favorites():
    favorites = defaultdict(list)
    for feed in models.Feed.objects():
        for article in feed.articles:
            if article.like:
                favorites[feed.title].append(article)

    return render_template('favorites.html', favorites=favorites)

@app.route('/management/', methods=['GET'])
def management():
    nb_article = len(models.Article.objects())
    return render_template('management.html', nb_article=nb_article)
#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, request, flash, session, url_for, redirect
from wtforms import TextField, PasswordField, SubmitField, validators
from flask.ext.mail import Message, Mail

#from forms import ContactForm, SignupForm, SigninForm
from pyaggr3g470r import app, db

import feedgetter
import models

mail = Mail()

@app.route('/')
def home():
    feeds = models.Feed.objects()
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
    return render_template('feedss.html', feeds=feeds)

@app.route('/feed/<feed_id>', methods=['GET'])
def feed(feed_id=None):
    feed = models.Watch.objects(id=feed_id).first()
    return render_template('feed.html', feed=feed)
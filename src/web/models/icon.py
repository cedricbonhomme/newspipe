#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bootstrap import db


class Icon(db.Model):
    url = db.Column(db.String(), primary_key=True)
    content = db.Column(db.String(), default=None)
    mimetype = db.Column(db.String(), default="application/image")

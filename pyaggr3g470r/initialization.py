#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""initialization.py

Initialization script.
"""

import sys
from mongoengine import *
from werkzeug import generate_password_hash

import conf
import models

if __name__ == "__main__":
    # Point of entry in execution mode
    firstname = sys.argv[1]
    lastname =  sys.argv[2]
    email = sys.argv[3]
    password = sys.argv[4]

    db = connect(conf.DATABASE_NAME)
    db.drop_database(conf.DATABASE_NAME)

    user = models.User(firstname=firstname, lastname=lastname, \
                email=email, pwdhash=generate_password_hash(password))
    user.save()
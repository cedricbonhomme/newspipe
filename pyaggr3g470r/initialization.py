#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""initialization.py

Initialization script.
"""

import sys
from mongoengine import *
from werkzeug import generate_password_hash

import models

if __name__ == "__main__":
    # Point of entry in execution mode
    database = sys.argv[1]
    firstname = sys.argv[2]
    lastname =  sys.argv[3]
    email = sys.argv[4]
    password = sys.argv[5]

    db = connect(database)
    db.drop_database(database)

    user = models.User(firstname=firstname, lastname=lastname, \
                email=email, pwdhash=generate_password_hash(password))
    user.save()
#! /usr/bin/env python
#-*- coding: utf-8 -*-

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
__version__ = "$Revision: 0.3 $"
__date__ = "$Date: 2012/10/12 $"
__revision__ = "$Date: 2013/01/14 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

import cherrypy
import hashlib

import log

SESSION_KEY = '_cp_username'

import csv
class excel_french(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\n'
    quoting = csv.QUOTE_MINIMAL

csv.register_dialect('excel_french', excel_french)

def change_username(username, new_username, password_file='./var/password'):
    """
    Change the password corresponding to username.
    """
    users_list = []
    result = False
    with open(password_file, 'r') as csv_readfile_read:
        cr = csv.reader(csv_readfile_read, 'excel_french')
        users_list = [elem for elem in cr]
    with open(password_file, 'w') as csv_file_write:
        cw = csv.writer(csv_file_write, 'excel_french')
        for user in users_list:
            if user[0] == username:
                cw.writerow([new_username, user[1]])
                result = True
            else:
                cw.writerow(user)
    return result

def change_password(username, new_password, password_file='./var/password'):
    """
    Change the password corresponding to username.
    """
    users_list = []
    result = False
    with open(password_file, 'r') as csv_readfile_read:
        cr = csv.reader(csv_readfile_read, 'excel_french')
        users_list = [elem for elem in cr]
    with open(password_file, 'w') as csv_file_write:
        cw = csv.writer(csv_file_write, 'excel_french')
        for user in users_list:
            if user[0] == username:
                m = hashlib.sha1()
                m.update(new_password.encode())
                cw.writerow([user[0], m.hexdigest()])
                result = True
            else:
                cw.writerow(user)
    return result

def check_credentials(username, password, password_file='./var/password'):
    """
    Verifies credentials for username and password.
    Returns None on success or a string describing the error on failure.
    """
    USERS = {}
    cr = csv.reader(open(password_file, "r"), 'excel_french')
    for row in cr:
        USERS[row[0]] = row[1]

    m = hashlib.sha1()
    m.update(password.encode())
    if username in list(USERS.keys()) and USERS[username] == m.hexdigest():
        return None
    else:
        return "Incorrect username or password."
    # An example implementation which uses an ORM could be:
    # u = User.get(username)
    # if u is None:
    #     return u"Username %s is unknown to me." % username
    # if u.password != md5.new(password).hexdigest():
    #     return u"Incorrect password"

def check_auth(*args, **kwargs):
    """
    A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill.
    """
    conditions = cherrypy.request.config.get('auth.require', None)
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    raise cherrypy.HTTPRedirect("/auth/login")
        else:
            raise cherrypy.HTTPRedirect("/auth/login")

cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

def require(*conditions):
    """
    A decorator that appends conditions to the auth.require config
    variable.
    """
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate


# Conditions are callables that return True
# if the user fulfills the conditions they define, False otherwise
#
# They can access the current username as cherrypy.request.login
#
# Define those at will however suits the application.

def member_of(groupname):
    def check():
        # replace with actual check if <username> is in <groupname>
        return cherrypy.request.login == 'joe' and groupname == 'admin'
    return check

def name_is(reqd_username):
    return lambda: reqd_username == cherrypy.request.login

# These might be handy

def any_of(*conditions):
    """
    Returns True if any of the conditions match.
    """
    def check():
        for c in conditions:
            if c():
                return True
        return False
    return check

# By default all conditions are required, but this might still be
# needed if you want to use it inside of an any_of(...) condition
def all_of(*conditions):
    """
    Returns True if all of the conditions match.
    """
    def check():
        for c in conditions:
            if not c():
                return False
        return True
    return check


class AuthController(object):
    """
    This class provides login and logout actions.
    """
    def __init__(self):
        self.logger = log.Log()
        self.username = ""

    def on_login(self, username):
        """
        Called on successful login.
        """
        self.username = username
        self.logger.info(username + ' logged in.')

    def on_logout(self, username):
        """
        Called on logout.
        """
        self.logger.info(username + ' logged out.')
        self.username = ""

    def get_loginform(self, username, msg="Enter login information", from_page="/"):
        """
        Login page.
        """
        return """<!DOCTYPE html>\n<html>
    <head>
        <meta charset="utf-8" />
        <title>pyAggr3g470r</title>
        <link rel="stylesheet" href="/css/log.css" />
    </head>
    <body>
        <div>
            <div id="logform">
                <img src="/static/img/tuxrss.png" alt="pyAggr3g470r" />
                <form method="post" action="/auth/login">
                    <input type="hidden" name="from_page" value="%(from_page)s" />
                    %(msg)s<br />
                    <input type="text" name="username" value="%(username)s" placeholder="Username" autofocus="autofocus" /><br />
                    <input type="password" name="password" placeholder="Password" /><br />
                    <input type="submit" value="Log in" />
                </form>
            </div><!-- end #main -->
        </div><!-- end #center -->
    </body>
</html>""" % locals()

    @cherrypy.expose
    def login(self, username=None, password=None, from_page="/"):
        """
        Open a session for an authenticated user.
        """
        if username is None or password is None:
            return self.get_loginform("", from_page=from_page)

        error_msg = check_credentials(username, password)
        if error_msg:
            self.logger.info(error_msg)
            return self.get_loginform(username, error_msg, from_page)
        else:
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            self.on_login(username)
            raise cherrypy.HTTPRedirect(from_page or "/")

    @cherrypy.expose
    def logout(self, from_page="/"):
        """
        Cloase a session.
        """
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(from_page or "/")
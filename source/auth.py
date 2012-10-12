#! /usr/bin/env python
#-*- coding: utf-8 -*-
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




def check_credentials(username, password):
    """Verifies credentials for username and password.
    Returns None on success or a string describing the error on failure"""
    # Adapt to your needs
    USERS = {}
    cr = csv.reader(open("./var/password", "r"), 'excel_french')
    for row in cr:
        USERS[row[0]] = row[1]

    m = hashlib.sha1()
    m.update(password)
    if username in USERS.keys() and USERS[username] == m.hexdigest():
        return None
    else:
        return u"Incorrect username or password."

    # An example implementation which uses an ORM could be:
    # u = User.get(username)
    # if u is None:
    #     return u"Username %s is unknown to me." % username
    # if u.password != md5.new(password).hexdigest():
    #     return u"Incorrect password"

def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill"""
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
    """A decorator that appends conditions to the auth.require config
    variable."""
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
    """Returns True if any of the conditions match"""
    def check():
        for c in conditions:
            if c():
                return True
        return False
    return check

# By default all conditions are required, but this might still be
# needed if you want to use it inside of an any_of(...) condition
def all_of(*conditions):
    """Returns True if all of the conditions match"""
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
        msg = ""
        return """<html>
    <head>
        <link rel="stylesheet" type="text/css" href="/css/style.css" />
    </head>
    <body>
        <img src="/img/tuxrss.png" alt="pyAggr3g470r" />
        <div id="center">
        <div id="main">
        <form method="post" action="/auth/login">
            <input type="hidden" name="from_page" value="%(from_page)s" />
            %(msg)s<br />
            <input type="text" name="username" value="%(username)s" placeholder="Username" /><br />
            <input type="password" name="password" placeholder="Password" /><br />
            <input type="submit" value="Log in" />
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

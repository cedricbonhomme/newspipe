#! /usr/local/bin/python
#-*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2010/29/01 $"
__copyright__ = "Copyright (c) 2010 Cedric Bonhomme"
__license__ = "GPLv3"

import sqlite3
import cherrypy
import ConfigParser

from cherrypy.lib.static import serve_file

config = ConfigParser.RawConfigParser()
config.read("./cfg/pyAggr3g470r.cfg")
path = config.get('global','path')

bindhost = "0.0.0.0"

cherrypy.config.update({ 'server.socket_port': 12556, 'server.socket_host': bindhost})

path = { '/css/style.css': {'tools.staticfile.on': True, 'tools.staticfile.filename':path+'css/style.css'}
             }

htmlheader = """<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
                lang="en">\n<head>\n<link rel="stylesheet" type="text/css" href="/css/style.css"
                />\n<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n
                <title>pyAggr3g470r - RSS Feed Reader</title> </head>"""

htmlfooter =  """</div></body></html>"""

htmlnav = """<body><h1><a href="/">pyAggr3g470r - RSS Feed Reader</a></h1><a
href="http://bitbucket.org/cedricbonhomme/pyaggr3g470r/">pyAggr3g470r (source code)</a>
"""


class Root:
    def index(self):
        html = htmlheader
        html += htmlnav
        html += """<br/><div class="right inner">"""
        html += """<h2>Search</h2>"""
        html += """<form method=get action="q/"><input type="text" name="v" value=""> <input
        type="submit" value="search"></form>"""
        html += """<a href="f/">Management of feed</a>"""
        html += """</div> <div class="left inner">"""


        dic = self.retrieve_feed()
        for rss_feed in dic.keys():
            html += '<h2><a href="' + rss_feed.encode('utf-8') + \
                    '">' + dic[rss_feed][0][1].encode('utf-8') + "</a></h2>"

            for article in dic[rss_feed]:
                html += '<a href="' + article[3].encode('utf-8') + \
                     '">' + article[2].encode('utf-8') + "</a><br />"

        html += htmlfooter
        return html

    def f(self):
        """
        """
        return "Hello world !"


    def retrieve_feed(self):
        conn = sqlite3.connect("./var/feed.db", isolation_level = None)
        c = conn.cursor()
        list_of_articles = c.execute("SELECT * FROM rss_feed").fetchall()
        c.close()

        dic = {}
        for article in list_of_articles:
            if article[2] not in dic:
                dic[article[2]] = [(article[0], article[1], article[3], article[4])]
            else:
                dic[article[2]].append((article[0], article[1], article[3], article[4]))

        return dic

    index.exposed = True
    f.exposed = True



if __name__ == '__main__':
    root = Root()
    cherrypy.quickstart(root, config=path)
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

from datetime import datetime
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
                html += article[0].encode('utf-8') + " - " + \
                        '<a href="' + article[3].encode('utf-8') + \
                        '">' + article[2].encode('utf-8') + "</a><br />"

        html += htmlfooter
        return html

    def f(self):
        """
        """
        return "Hello world !"


    def retrieve_feed(self):
        list_of_articles = None
        try:
            conn = sqlite3.connect("./var/feed.db", isolation_level = None)
            c = conn.cursor()
            list_of_articles = c.execute("SELECT * FROM rss_feed").fetchall()
            c.close()
        except:
            pass

        if list_of_articles is not None:
            dic = {}
            for article in list_of_articles:
                if article[2] not in dic:

                    dic[article[2]] = [(article[0], article[1], article[3], article[4])]
                else:
                    dic[article[2]].append((article[0], article[1], article[3], article[4]))

            # sort articles by date for each feeds
            for feeds in dic.keys():
                dic[feeds].sort(lambda x,y: compare(y[0], x[0]))

            return dic
        return {}

    index.exposed = True
    f.exposed = True


def compare(stringtime1, stringtime2):
    """
    Compare two dates in the format 'yyyy-mm-dd hh:mm:ss'.
    """
    date1, time1 = stringtime1.split(' ')
    date2, time2 = stringtime2.split(' ')

    year1, month1, day1 = date1.split('-')
    year2, month2, day2 = date2.split('-')

    hour1, minute1, second1 = time1.split(':')
    hour2, minute2, second2 = time2.split(':')

    datetime1 = datetime(year=int(year1), month=int(month1), day=int(day1), \
                        hour=int(hour1), minute=int(minute1), second=int(second1))

    datetime2 = datetime(year=int(year2), month=int(month2), day=int(day2), \
                        hour=int(hour2), minute=int(minute2), second=int(second2))

    if datetime1 < datetime2:
        return -1
    elif datetime1 > datetime2:
        return 1
    else:
        return 0


if __name__ == '__main__':
    root = Root()
    cherrypy.quickstart(root, config=path)
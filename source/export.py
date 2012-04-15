#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010  Cédric Bonhomme - http://cedricbonhomme.org/
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
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2011/10/24 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

#
# This file contains the export functions of pyAggr3g470r. Indeed
# it is possible to export the database of articles in different formats:
# - simple HTML webzine;
# - text file;
# - ePub file;
# - PDF file.
#

import os
import hashlib

import utils


htmlheader = '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n' + \
        '<head>' + \
        '\n\t<title>pyAggr3g470r - News aggregator</title>\n' + \
        '\t<link rel="stylesheet" type="text/css" href="/css/style.css" />' + \
        '\n\t<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n' + \
        '</head>\n'

htmlfooter = '<p>This software is under GPLv3 license. You are welcome to copy, modify or' + \
            ' redistribute the source code according to the' + \
            ' <a href="http://www.gnu.org/licenses/gpl-3.0.txt">GPLv3</a> license.</p></div>\n' + \
            '</body>\n</html>'



def export_html(feeds):
    """
    Export the articles given in parameter in a simple Webzine.
    """
    index = htmlheader
    index += "<br />\n<ul>"
    for feed in feeds.values():
        # creates a folder for each stream
        feed_folder = utils.path + "/var/export/webzine/" + \
                utils.normalize_filename(feed.feed_id)
        try:
            os.makedirs(feed_folder)
        except OSError:
            # directories already exists (not a problem)
            pass


        index += """<li><a href="%s">%s</a></a></li>\n""" % \
                        (feed.feed_id, feed.feed_title)

        posts = htmlheader
        for article in feed.articles.values():

            post_file_name = os.path.normpath(feed_folder + "/" + article.article_id + ".html")
            feed_index = os.path.normpath(feed_folder + "/index.html")

            posts += article.article_date + " - " + \
                    """<a href="./%s.html">%s</a>""" % \
                            (article.article_id, article.article_title[:150]) + "<br />\n"


            a_post = htmlheader
            a_post += '\n<div style="width: 50%; overflow:hidden; text-align: justify; margin:0 auto">\n'
            a_post += """<h1><a href="%s">%s</a></h1><br />""" % \
                        (article.article_link, article.article_title)
            a_post += article.article_description
            a_post += "</div>\n<hr />\n"
            a_post += """<br />\n<a href="%s">Complete story</a>\n<br />\n""" % (article.article_link,)
            a_post += "<hr />\n" + htmlfooter


            with open(post_file_name, "w") as f:
                f.write(a_post)

        posts +=  htmlfooter
        with open(feed_index, "w") as f:
            f.write(posts)

    index += "\n</ul>\n<br />"
    index += htmlfooter
    with open(utils.path + "/var/export/webzine/" + "index.html", "w") as f:
        f.write(index)

def export_txt(feeds):
    """
    Export the articles given in parameter in text files.
    """
    for feed in feeds.values():
            # creates folder for each stream
            folder = utils.path + "/var/export/txt/" + \
                    utils.normalize_filename(feed.feed_title.strip().replace(':', '').lower())
            try:
                os.makedirs(folder)
            except OSError:
                # directories already exists (not a problem)
                pass

            for article in feed.articles.values():
                name = article.article_date.strip().replace(' ', '_')
                name = os.path.normpath(folder + "/" + name + ".txt")

                content = "Title: " + article.article_title + "\n\n\n"
                content += utils.clear_string(article.article_description)

                with open(name, "w") as f:
                    f.write(content)

def export_epub(feeds):
    """
    Export the articles given in parameter in ePub files.
    """
    from epub import ez_epub
    for feed in feeds.values():
            # creates folder for each stream
            folder = utils.path + "/var/export/epub/" + \
                    utils.normalize_filename(feed.feed_title.strip().replace(':', '').lower())
            try:
                os.makedirs(folder)
            except OSError:
                # directories already exists (not a problem)
                pass

            for article in feed.articles.values():
                name = article.article_date.strip().replace(' ', '_')
                name = os.path.normpath(folder + "/" + name + ".epub")

                section = ez_epub.Section()
                section.title = article.article_title.decode('utf-8')
                section.paragraphs = [utils.clear_string(article.article_description).decode('utf-8')]
                ez_epub.makeBook(article.article_title.decode('utf-8'), [feed.feed_title.decode('utf-8')], [section], \
                                    name, lang='en-US', cover=None)

def export_pdf(feeds):
    """
    Export the articles given in parameter in PDF files.
    """
    from xhtml2pdf import pisa
    import cStringIO as StringIO
    for feed in feeds.values():
            # creates folder for each stream
            folder = utils.path + "/var/export/pdf/" + \
                    utils.normalize_filename(feed.feed_title.strip().replace(':', '').lower())
            try:
                os.makedirs(folder)
            except OSError:
                # directories already exists (not a problem)
                pass

            for article in feed.articles.values():
                name = article.article_date.strip().replace(' ', '_')
                name = os.path.normpath(folder + "/" + name + ".pdf")
                
                content = htmlheader
                content += '\n<div style="width: 50%; overflow:hidden; text-align: justify; margin:0 auto">\n'
                content += """<h1><a href="%s">%s</a></h1><br />""" % \
                            (article.article_link, article.article_title)
                content += article.article_description
                content += "</div>\n<hr />\n"
                content += htmlfooter

                try:
                    pdf = pisa.CreatePDF(StringIO.StringIO(content), file(name, "wb"))
                except:
                    pass
#! /usr/bin/env python
#-*- coding: utf-8 -*-

import os
import hashlib

import utils


htmlheader = '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n' + \
        '<head>' + \
        '\n\t<title>pyAggr3g470r - News aggregator</title>\n' + \
        '\t<link rel="stylesheet" type="text/css" href="/css/style.css" />' + \
        '\n\t<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n' + \
        '\n\t<script type="text/javascript" src="https://apis.google.com/js/plusone.js"></script>\n' + \
        '</head>\n'

htmlfooter = '<p>This software is under GPLv3 license. You are welcome to copy, modify or' + \
            ' redistribute the source code according to the' + \
            ' <a href="http://www.gnu.org/licenses/gpl-3.0.txt">GPLv3</a> license.</p></div>\n' + \
            '</body>\n</html>'



def export_webzine(feeds):
    """
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

        
def exports(feeds, export_method):
    for feed in self.feeds.values():
            # creates folder for each stream
            folder = utils.path + "/var/export/" + \
                    utils.normalize_filename(feed.feed_title.strip().replace(':', '').lower())
            try:
                os.makedirs(folder)
            except OSError:
                # directories already exists (not a problem)
                pass

            for article in feed.articles.values():
                name = article.article_date.strip().replace(' ', '_')

                # Export all articles in HTML format
                if export_method == "export_HTML":
                    name = os.path.normpath(folder + "/" + name + ".html")
                    content = htmlheader()
                    content += '\n<div style="width: 50%; overflow:hidden; text-align: justify; margin:0 auto">\n'
                    content += """<h1><a href="%s">%s</a></h1><br />""" % \
                                (article.article_link, article.article_title)
                    content += article.article_description
                    content += "</div>\n<hr />\n"
                    content += htmlfooter

                # Export for dokuwiki
                # example: http://wiki.cedricbonhomme.org/doku.php/news-archives
                elif export_method == "export_dokuwiki":
                    name = os.path.normpath(folder + "/" + name.replace(':', '-') + ".txt")
                    content = "<html>"
                    content += '\n<div style="width: 50%; overflow:hidden; text-align: justify; margin:0 auto">\n'
                    content += """<h1><a href="%s">%s</a></h1><br />""" % \
                                (article.article_link, article.article_title)
                    content += article.article_description
                    content += '</div>\n<hr />Generated with <a href="http://bitbucket.org/cedricbonhomme/pyaggr3g470r/">pyAggr3g470r</a>\n</html>'

                # Export all articles in raw text
                elif export_method == "export_TXT":
                    content = "Title: " + article.article_title + "\n\n\n"
                    content += utils.clear_string(article.article_description)
                    name = os.path.normpath(folder + "/" + name + ".txt")

                with open(name, "w") as f:
                    f.write(content)
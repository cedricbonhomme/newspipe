            pyAggr3g470r project news

5.5: 14 Jun 2014 13:09
    This release introduces a redesigned homepage which loads much faster and
    is easier to read. pyAggr3g470r can now be run by Apache.
    Adding a feed no longer requires a title and a site link.

5.4: 28 May 2014 05:16
    This version makes it possible for a user to export all of their feeds and
    articles as a JSON file for later restoration.

5.3: 23 May 2014 22:39
    This release introduces some UI improvements, especially for the home page.

5.2: 16 May 2014 17:23
    This release adds minor bug fixes and UI improvements.

5.1: 13 May 2014 20:58
    When deployed on Heroku, the platform now uses the Postmark service to
    send account confirmation emails to users. It is no longer required to
    enter a first name and a last name to create an account.

5.0: 04 May 2014 20:54
    pyAggr3g470r is now translated into English and French. Improvements
    concerning the news retriever and the Whoosh search functionality have
    been made. The user can now export all articles in JSON format.
    The user of the platform now has the possibility to delete his or her
    account.

4.9: 24 Apr 2014 21:11
    This version introduces minor improvements to the Jinja templates and
    bugfixes (relating to the import of OPML files with sub-categories and
    relating to the Whoosh index generation).

4.8: 13 Apr 2014 11:35
    Feeds are now retrieved in a separated process with the Gevent library.
    This offers the best performance on Heroku.

4.7: 12 Apr 2014 12:24
    pyAggr3g470r can now be deployed on Heroku or on a traditional server.
    Moreover, several users can use an instance of pyAggr3g470r. A platform is
    managed by the administrator, a user with specific rights.

4.6: 09 Feb 2014 21:23
    This release introduces the import of OPML files of subscriptions.
    Minor improvements have been made to the templates.
    
4.5: 29 Jan 2014 17:40
    This release introduces a one step installation process with a simple
    script. Minor improvements to the feedgetter module have been introduced
    (the feed description is now stored in the database). Miscellaneous
    improvements to the Jinja templates. Finally, more configuration options
    are now offered to the user.

4.4: 27 Dec 2013 23:10
    This version introduces some improvements for the feedgetter module
    including automatic retrieval of the URL behind feedproxy.google.com,
    and support for configuring the user agent and proxy. Minor improvements
    were made to the MongoEngine models. Notifications are displayed with
    Flask flash messages.

4.3: 03 Dec 2013 21:27
    With this release, the user is able to update her personal information.
    It is now possible to enable/disable the checking of updates for a feed.
    Some performance improvements and user interface optimizations have been
    done.

4.2: 10 Nov 2013 00:11
    This is the first release of the new version of pyAggr3g470r.
    The code has been rewritten with the Flask microframework and the
    Bootstrap frontend framework.

4.1: 11 Aug 2013 13:19
    HTTP proxy support has been added for the fetching of feeds. This is
    useful, for example, if you are using Privoxy/Tor.

4.0: 25 Jun 2013 11:42
    Searching of articles is now achieved with Whoosh, a fast full-text
    indexing and searching library.

3.9: 14 Apr 2013 19:40
    The code has been tested and ported to Python 3.3.1. Some minor bugs have
    been fixed, with a lot of improvements concerning the Mako templates,
    MongoDB database management, and management of exceptions.

3.8: 12 Jan 2013 11:07
    This release introduces a reworked management page; it is now possible to
    change the username and password via this page.
    Some improvements concerning the HTML export of the database have been
    made. Finally, indexed MongoDB full text searching provides a much faster
    search.

3.7: 29 Dec 2012 22:10
    pyAggr3g470r is now using the Mako template library.
    Performance improvements for the MongoDB database have been made, and some
    minor bugfixes. Stop words (a, of, the, an, for...) are now ignored when
    calculating top words for the generation of the tag cloud.
    A new page indicates the list of inactive feeds (with no new published
    articles since a given number of days).

3.6: 08 Nov 2012 22:56
    pyAggr3g470r is now running with Python 3.2(.3). It uses CherryPy 3.2.2,
    BeautifulSoup4, and feedparser3.Your old MongoDB database can be used
    without any problem.

3.5 :28 Oct 2012 13:37
    Some minor bugfixes and improvements.
    An authentication screen has been added, which is useful if pyAggr3g470r
    is running on an EC2 instance, for example.

3.4: 01 May 2012 16:50
    This version introduces some minor improvements and bugfixes.
    All features of pyAggr3g470r are now back (with MongoDB).

3.3: 16 Apr 2012 20:40
    This version introduces minor improvements and a bugfix.
    Publication dates of articles are now stored as a datetime object.
    A bug in the script that converts an SQLite database to a MongoDB database
    is now fixed.
    A little documentation has been added.

3.2: 20 Mar 2012 20:59
    A MongoDB database is now used instead of the SQLite database. This change
    offers a significant performance improvement. The database has been tested
    with more than 30,000 articles, but version 3.2 is still a test version.
    A more stable version will arrive soon.

3.1: 29 Nov 2011 06:54
    A new version of the QR Code module is used. For each article, a QR Code
    is generated based on the content of the article. If the article is too
    long, only the article's URL is encoded in the QR Code. For a given
    string, the algorithm tries the generate as small a QR Code as possible.
    Minor bugs were fixed.

3.0: 25 Oct 2011 12:52
    This release introduces exportation of articles to the HTML format and to
    the PDF format (there is still exportation to ePub).
    The sharing of articles with delicious.com was replaced by pinboard.in.s

2.9: 26 Aug 2011 17:43
    Some minor improvements. A bug with the HTML <code> tag bas been fixed.
    Cleanup was done with Pylint.
    The test database of pyAggr3g470r contains more than 22000 articles,
    and it runs perfectly.

2.8: 08 Jul 2011 06:55
    The feed summary page, which displays general information about a feed,
    now lets you change the feed metadata (feed logo, feed name, and feed URL
    if changed). Moreover, this page displays the activity of a feed and other
    useful information. It is now possible to set a different POD for Diaspora
    in the configuration file and to share an article with Google +1.
    A control file to start or stop pyAggr3g470r has been added.
    From the GUI side, a new transparent CSS tooltip has been introduced in
    order to preview an article.
    Finally, some minor performance improvements and bugfixes were made.

2.7: 15 Apr 2011 20:46
    Minor improvements.
    It is now possible to set a maximum number of articles to be loaded from
    the database for each feed (via the management page).

2.6: 21 Mar 2011 17:21
    This version introduces a new page that displays general information about
    a feed. There are some minor improvements in the Web interface.
    The version of pyAggr3g470r for Python 3 is now fully ready and has been
    tested with Python 3.2.
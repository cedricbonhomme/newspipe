            pyAggr3g470r project news

6.7: 2015-07-21
    New:
     * a filter mechanism for feeds has been added (PR #14);
     * icon of feeds is now an url retrieved from the feed or the site link (PR #15).
    Improvements:
     * improvements for the bookmarklet (PR #16 and PR #18);
     * performance improvements (display of the /feed page);
     * enhancements for the two crawlers;
     * enhancements of the UI (PR #14);
     * misc changes to the models and controllers.

6.6: 2015-06-02
    New:
     * it is now possible to sort the list of articles by feed title or
     article title;
     * added base unittests.
    Improvements:
     * fixed some minor bugs;
     * improved the asyncio crawler;
     * automatically use the good Python executable for the asyncio crawler;
     * improved controllers (enforcing better use of user_id);
     * the search is now case insensitive.

6.5.5: 2015-04-22
    The full text search powered by Whoosh has been removed.

6.5.4: 2015-04-16
    This release introduces a new config module and a new search functionality.
    The result of a search is integrated in the main page.

6.5.3: 2015-04-14
    The fetch call is now dependent to the selected crawling method.

6.5.2: 2015-04-14
    The look and feel has been globally improved.
    It is now possible to add a new feed from any page via a dropdown menu.

6.5.1: 2015-04-08
    Improvements:
     * improvements on the controllers;
     * the minimum error count is now specified in the configuration file.

6.5: 2015-04-07
    Improvements:
     * new CSS;
     * improved installation script;
     * it is now possible to delete all duplicate articles with one HTTP
     delete request.

6.4: 2015-03-17
    New:
     * a new page 'history' to explore your database of articles.
    Changes:
     * updated documentation;
     * minor improvements.
    Fixes:
     * changed the type of the column 'last_modified' to string.

6.3: 2015-03-08
    New:
    * a new architecture with base for controllers;
    * new, more complete RESTful API;
    * a crawler handling errors and cache control;
    * the new crawler takes advantage of the RESTful API
    (can be run on the client side).

6.2: 2015-02-26
    The system of email notifications for new articles has been removed.
    This feature was hardly used.

6.1: 2015-02-23
    Improvements: articles are now identified with the id provided
    by the RSS/ATOM feed.
    Prevent BeautifulSoup4 from adding extra '<html><body>' tags to
    the soup with the 'lxml' parser.
    Indexation is now used with the new crawler.
    The documentation has been updated.

6.0: 2015-02-08
    New: pyAggr3g470r is now working with Python 3.4. Tested on Heroku
    with Python 3.4.2.
    Improvements: The feed crawler uses the PEP 3156 (asyncio). The action
    buttons are now on the left. It is easier to mark an article as read.

5.7.0: 2014-11-20
    Improvements: major improvements of the email notifications system.
    Notifications are now sent through Postmark (for example for Heroku)
    or a standard SMTP server.
    Bug fix: activation key was too long for the database column.

5.6.6: 2014-09-24
    Improvements: Significant performance improvement for the views
    /favorites and /unread. The performance problem has been introduced
    with the release 5.6.5.

5.6.5: 2014-09-15
    This release fixes a major bug introduced with the version 0.9.7 of SQLAlchemy
    (conflicts between persistent ant transcient SQLAlchemy objects).

5.6.4: 2014-09-12
    Translations have been updated.
    Gravatar extension has been removed.
    Minor fix.

5.6.3: 2014-08-27
    News: It is now possible to delete articles older than a given number
    of weeks. This can be done via the management page.
    A new environment variable enables to activate or deactivate the
    self-registration.
    Changes: translations were updated. Some minor bugfixes. Improved
    deployment instructions in the README.

5.6.2: 2014-08-10
    Minor improvements: Articles are automatically retrieved after the import
    of an OPML file.
    When displaying all articles (unread + read), titles of unread articles
    are emphasized in bold.
    A new tab is opened when clicking on the title of an article.
    New: pyAggr3g470r can be deployed with the Heroku auto deploy button.

5.6.1: 2014-07-13
    Performance improvements: faster database insertion of articles by
    the crawler and loading of the management page.
    Minor bug fixes.

5.6: 2014-07-05
    pyAggr3g470r has now a RESTful JSON API which enables to manage Feed and
    Article objects. The API is documented in the README file.
    The main page is using a subset of this API with jQuery HTTP requests.

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

2.5: 19 Jan 2011 07:16
    A bug when removing a feed from the data base was fixed.
    Minor improvements were made for export of articles and the size of HTML
    forms.

2.4: 07 Dec 2010 18:02
    The GUI uses more HTML 5 features like HTML5 Forms Validation
    (email input, URL input), an HTML5 month+year date picker, and a
    placeholder. From each article it is possible to access the
    following and previous article (and a new main menu with CSS ToolTip).
    Articles can now be exported to the EPUB format. Articles loaded from the
    SQLite base are now stored in memory in a better data structure. With more
    than 10,000 articles, pyAggr3g470r starts in 3 seconds. Finally, email
    notifications are now sent with HTML message content and with an
    alternative plain text version (MIMEMultipart).

2.3: 15 Nov 2010 22:05
    This version introduces HTML5 Forms Validation and a HTML5 month+year date
    picker for the history page, which can be used to search for articles.
    This currently only works with Opera.

2.2: 03 Nov 2010 19:31
    There is now a third way to export articles from the SQLite base.
    There is an export method for the wiki DokuWiki (example in the commit
    message).

2.1: 25 Oct 2010 15:56
    The export of articles to HTML has been updated, with better output.
    There are a number of improvements (the search function, generation of
    tags cloud, display of article content, CSS, bugfixes, etc.).
    There is a new Wiki.

2.0: 03 Sep 2010 19:04
    It is now possible to browse articles by year and month with tag clouds
    (see new screenshots).
    In addition, URL errors are detected before downloading feeds.
    There are some improvements in the user interface.

1.9: 02 Sep 2010 09:17
    The feedgetter module was improved. More details about articles are stored
    in the database when possile. An attempt is made to get the whole article
    (a_feed['entries'][i].content[j].value), and in the event of failure,
    the description/summary is used (a_feed['entries'][i].description).

1.8: 25 Aug 2010 06:47
    It is now easier to install pyAggr3g470r.
    There is no longer any need to set any path in the configuration file.

1.7: 23 Jul 2010 11:21
    This release generates QR codes with URLs of articles, so you can read an
    article later on your smartphone (or share with friends).

1.6: 08 Jul 2010 11:27
    It is now possible to automatically add a feed (with the URL of the site),
    delete an article, delete a feed with all its articles, and to delete all
    articles from the database.
    There are also some nice improvements to performance, tested with more
    than 3000 articles.
    Furthermore, HTML export of all the articles of the database was improved.
    You can also export the articles in raw text. Finally, some minor bugs
    were fixed.

1.5: 05 Jul 2010 09:17
    Now pyAggr3g470r only works with Python 2.7.
    OrderedDict objects are used in order to sort the feeds alphabetically in
    a simple way.

1.4: 10 Jun 2010 12:09
    It is now possible to remove all articles of a given feed from the SQLite
    base via the management page. You can also add a feed just with the URL
    of the Web page. The URL of the feed is obtained by parsing the Web page
    with the module BeautifulSoup.

1.3: 04 May 2010 06:12
    All articles stored in the SQLite database can now be exported as HTML or
    raw text via the management page.

1.2: 29 Apr 2010 07:41
    This version introduces a tag cloud with variable word length.
    Some improvements were made to the CSS and a bug was fixed.

1.1: 15 Apr 2010 19:09
    Introduction of a Google Buzz button.
    It is now possible to mark or unmark articles as favorites.

1.0: 23 Mar 2010 14:40
    The database of feeds is monitored with the Python gamin module,
    if present. Otherwise it is done with a classic function.
    You now have the option to be informed of new articles by email. To
    receive these notifications, just click on "Stay tuned" for the
    desired feed(s) at the main page of pyAggr3g470r in the browser.

0.9: 28 Feb 2010 18:37
    TuxDroid tells you when there are unread articles (this module is
    independent in case you don't have a TuxDroid). Moreover, the language of
    articles is detected (thanks to the oice.langdet Python module). This
    allows you to search for articles by language.

0.8: 24 Feb 2010 11:56
    It is now possible to share articles with delicious, Digg, reddit,
    Scoopeo, and Blogmarks.
    The "Management of feeds" page presents information on the database and
    statistics on articles (with a histogram). HTML tags are now skipped for
    the search. Some other improvements were made.

0.7: 15 Feb 2010 16:36
    It is now possible to search for an article, through the titles and
    descriptions.

0.6: 05 Feb 2010 23:01
    Unread articles are now shown in bold. This was implemented using a new
    field in the SQLite database. New tabs for article descriptions are opened
    with the _rel=noreferrer_ option in order to separate processes (useful
    with Chromium). It is now possible to see only unread articles for each feed.

0.5: 02 Feb 2010 21:41
    It is now possible to fetch feeds manually by clicking on "Fetch all feeds"
    and/or with cron. Better navigation between feeds and improvements to the
    SQLite database have been added.

0.4: 01 Feb 2010 22:05
    Release 0.4. The main page display only 10 articles by feeds.
    For each feeds a page present the list of all articles. The SQLite base is
    smaller than before (removed hashed value).
    A lot of improvements.

0.3: 01 Feb 2010 11:50
    A new menu was added for faster access to feeds. Some improvements were
    made to the CSS.

0.2: 31 Jan 2010 21:10
    Articles are now sorted by date, and it is possible to read just a
    description of an article. There are some improvements in the code and
    SQLite base management.

0.1: 29 Jan 2010 21:09
    First release of pyAggr3g470r.

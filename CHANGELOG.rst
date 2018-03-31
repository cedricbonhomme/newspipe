=================
Release History
=================

8.0 (2017-05-24)
----------------
    New:
     * you can now manage your bookmarks with Newspipe;
     * a bookmarklet is available in order to quickly bookmark Web pages;
     * import of bookmarks from Pinboard (JSON export);
     * new logo;
    Improvements:
     * refactoring and code cleaning;
     * improved Heroku auto-deploy functionality.
    Fixes:
     * crawler: argument of type 'NoneType' is not iterable in html.unescape().

7.1.3 (2016-11-14)
------------------
    New:
     * a template for the articles of public feeds has been added;
     * the template of the feeds is now also used for users who are not
       authenticated (if the feed is not private);
     * tags of articles are now displayed in the UI.
    Improvements:
     * it is now possible to configure the feeds refresh interval (in minutes)
       for the crawler (even if the crawler is used with cron);
     * various improvements to the UI of the public profile page;
     * simpler format for the logs when the application is running on Heroku.

7.1.2 (2016-11-08)
------------------
    New:
     * the new name of JARR is now Newspipe;
     * the user can now add its twitter link through the profile page;
     * it is now possible to edit the visibility of a feed (if it should be
       listed in the list of the user's public profile);
     * tags of articles are now retrieved in order to use k-means clustering
       on tags (will be faster than on the article's content);
     * various improvements to the crawler (test if an article should be
       updated and better use of coroutines).
    Improvements:
     * improved the layout of the profile page;
     * the React.js page now only lists the feeds with unread articles by
       default;
     * improvements for the crawler.
    Removal:
     * removed the 'refresh_rate' column from the user table;
     * removed the export to HTML webzine functionality.

7.1.1 (2016-10-04)
------------------
    Improvements:
     * improved the installation script;
     * improved the deployment process with Vagrant.
    Fixes:
     * fixed a bug that occurred when deleting a user who has categories with
       feeds in it;
     * fixed a bug that occurred when the user wants to use SQLite.

7.1 (2016-09-26)
----------------
    New:
     * public profile page for users (private by default);
     * popular page: displays the most popular feeds recentlty added by the users;
     * new logo.
    Improvements:
     * the profile edition page has been improved;
     * the generation of the tag cloud has been improved (faster).
    Fixes:
     * fixed a bug when loading the list of stop words.


7.0 (2016-04-07)
----------------
    New:
     * redoing entierly the home page with react;
     * implementing category;
     * the classic crawler is now taking into account updated articles from feeds;
     * support of HTTP proxy has been removed;
     * article URL resolving has been removed (wasn't used);
     * improvement of the management of users in the dashboard;
     * account confirmation is now achieved with a token that expires in a
       specified time.
    Improvements:
     * Code re-arangement: move all code to /src/

6.7 (2015-07-21)
----------------
    New:
     * a filter mechanism for feeds has been added (PR #14);
     * icon of feeds is now an url retrieved from the feed or the site link (PR #15).
    Improvements:
     * improvements for the bookmarklet (PR #16 and PR #18);
     * performance improvements (display of the /feed page);
     * enhancements for the two crawlers;
     * enhancements of the UI (PR #14);
     * misc changes to the models and controllers.

6.6 (2015-06-02)
----------------
    New:
     * it is now possible to sort the list of articles by feed title or article title;
     * added base unittests.
    Improvements:
     * fixed some minor bugs;
     * improved the asyncio crawler;
     * automatically use the good Python executable for the asyncio crawler;
     * improved controllers (enforcing better use of user_id);
     * the search is now case insensitive.

6.5.5 (2015-04-22)
------------------
    The full text search powered by Whoosh has been removed.

6.5.4 (2015-04-16)
------------------
    This release introduces a new config module and a new search functionality.
    The result of a search is integrated in the main page.

6.5.3 (2015-04-14)
------------------
    The fetch call is now dependent to the selected crawling method.

6.5.2 (2015-04-14)
------------------
    The look and feel has been globally improved.
    It is now possible to add a new feed from any page via a dropdown menu.

6.5.1 (2015-04-08)
------------------
    Improvements:
     * improvements on the controllers;
     * the minimum error count is now specified in the configuration file.

6.5 (2015-04-07)
----------------
    Improvements:
     * new CSS;
     * improved installation script;
     * it is now possible to delete all duplicate articles with one HTTP delete request.

6.4 (2015-03-17)
----------------
    New:
     * a new page 'history' to explore your database of articles.
    Changes:
     * updated documentation;
     * minor improvements.
    Fixes:
     * changed the type of the column 'last_modified' to string.

6.3 (2015-03-08)
----------------
    New:
    * a new architecture with base for controllers;
    * new, more complete RESTful API;
    * a crawler handling errors and cache control;
    * the new crawler takes advantage of the RESTful API
    (can be run on the client side).

6.2 (2015-02-26)
----------------
    The system of email notifications for new articles has been removed.
    This feature was hardly used.

6.1 (2015-02-23)
----------------
    Improvements: articles are now identified with the id provided
    by the RSS/ATOM feed.
    Prevent BeautifulSoup4 from adding extra '<html><body>' tags to
    the soup with the 'lxml' parser.
    Indexation is now used with the new crawler.
    The documentation has been updated.

6.0 (2015-02-08)
----------------
    New: pyAggr3g470r is now working with Python 3.4. Tested on Heroku
    with Python 3.4.2.
    Improvements: The feed crawler uses the PEP 3156 (asyncio). The action
    buttons are now on the left. It is easier to mark an article as read.

5.7.0 (2014-11-20)
------------------
    Improvements: major improvements of the email notifications system.
    Notifications are now sent through Postmark (for example for Heroku)
    or a standard SMTP server.
    Bug fix: activation key was too long for the database column.

5.6.6 (2014-09-24)
------------------
    Improvements: Significant performance improvement for the views
    /favorites and /unread. The performance problem has been introduced
    with the release 5.6.5.

5.6.5 (2014-09-15)
------------------
    This release fixes a major bug introduced with the version 0.9.7 of SQLAlchemy
    (conflicts between persistent ant transcient SQLAlchemy objects).

5.6.4 (2014-09-12)
------------------
    Translations have been updated.
    Gravatar extension has been removed.
    Minor fix.

5.6.3 (2014-08-27)
------------------
    News: It is now possible to delete articles older than a given number
    of weeks. This can be done via the management page.
    A new environment variable enables to activate or deactivate the
    self-registration.
    Changes: translations were updated. Some minor bugfixes. Improved
    deployment instructions in the README.

5.6.2 (2014-08-10)
------------------
    Minor improvements: Articles are automatically retrieved after the import
    of an OPML file.
    When displaying all articles (unread + read), titles of unread articles
    are emphasized in bold.
    A new tab is opened when clicking on the title of an article.
    New: pyAggr3g470r can be deployed with the Heroku auto deploy button.

5.6.1 (2014-07-13)
------------------
    Performance improvements: faster database insertion of articles by
    the crawler and loading of the management page.
    Minor bug fixes.

5.6 (2014-07-05)
----------------
    pyAggr3g470r has now a RESTful JSON API which enables to manage Feed and
    Article objects. The API is documented in the README file.
    The main page is using a subset of this API with jQuery HTTP requests.

5.5 (2014-06-14)
----------------
    This release introduces a redesigned homepage which loads much faster and
    is easier to read. pyAggr3g470r can now be run by Apache.
    Adding a feed no longer requires a title and a site link.

5.4 (2014-05-28)
----------------
    This version makes it possible for a user to export all of their feeds and
    articles as a JSON file for later restoration.

5.3 (2014-05-23)
----------------
    This release introduces some UI improvements, especially for the home page.

5.2 (2014-05-16)
----------------
    This release adds minor bug fixes and UI improvements.

5.1 (2014-05-13)
----------------
    When deployed on Heroku, the platform now uses the Postmark service to
    send account confirmation emails to users. It is no longer required to
    enter a first name and a last name to create an account.

5.0 (2014-05-04)
----------------
    pyAggr3g470r is now translated into English and French. Improvements
    concerning the news retriever and the Whoosh search functionality have
    been made. The user can now export all articles in JSON format.
    The user of the platform now has the possibility to delete his or her
    account.

4.9 (2014-04-24)
----------------
    This version introduces minor improvements to the Jinja templates and
    bugfixes (relating to the import of OPML files with sub-categories and
    relating to the Whoosh index generation).

4.8 (2014-04-13)
----------------
    Feeds are now retrieved in a separated process with the Gevent library.
    This offers the best performance on Heroku.

4.7 (2014-04-12)
----------------
    pyAggr3g470r can now be deployed on Heroku or on a traditional server.
    Moreover, several users can use an instance of pyAggr3g470r. A platform is
    managed by the administrator, a user with specific rights.

4.6 (2014-02-09)
----------------
    This release introduces the import of OPML files of subscriptions.
    Minor improvements have been made to the templates.

4.5 (2014-01-29)
----------------
    This release introduces a one step installation process with a simple
    script. Minor improvements to the feedgetter module have been introduced
    (the feed description is now stored in the database). Miscellaneous
    improvements to the Jinja templates. Finally, more configuration options
    are now offered to the user.

4.4 (2013-12-27)
----------------
    This version introduces some improvements for the feedgetter module
    including automatic retrieval of the URL behind feedproxy.google.com,
    and support for configuring the user agent and proxy. Minor improvements
    were made to the MongoEngine models. Notifications are displayed with
    Flask flash messages.

4.3 (2013-12-03)
----------------
    With this release, the user is able to update her personal information.
    It is now possible to enable/disable the checking of updates for a feed.
    Some performance improvements and user interface optimizations have been
    done.

4.2 (2013-11-10)
----------------
    This is the first release of the new version of pyAggr3g470r.
    The code has been rewritten with the Flask microframework and the
    Bootstrap frontend framework.

4.1 (2013-08-11)
----------------
    HTTP proxy support has been added for the fetching of feeds. This is
    useful, for example, if you are using Privoxy/Tor.

4.0 (2013-06-25)
----------------
    Searching of articles is now achieved with Whoosh, a fast full-text
    indexing and searching library.

3.9 (2013-04-14)
----------------
    The code has been tested and ported to Python 3.3.1. Some minor bugs have
    been fixed, with a lot of improvements concerning the Mako templates,
    MongoDB database management, and management of exceptions.

3.8 (2013-01-12)
----------------
    This release introduces a reworked management page; it is now possible to
    change the username and password via this page.
    Some improvements concerning the HTML export of the database have been
    made. Finally, indexed MongoDB full text searching provides a much faster
    search.

3.7 (2012-12-29)
----------------
    pyAggr3g470r is now using the Mako template library.
    Performance improvements for the MongoDB database have been made, and some
    minor bugfixes. Stop words (a, of, the, an, for...) are now ignored when
    calculating top words for the generation of the tag cloud.
    A new page indicates the list of inactive feeds (with no new published
    articles since a given number of days).

3.6 (2012-11-08)
----------------
    pyAggr3g470r is now running with Python 3.2(.3). It uses CherryPy 3.2.2,
    BeautifulSoup4, and feedparser3.Your old MongoDB database can be used
    without any problem.

3.5 (2012-10-28)
----------------
    Some minor bugfixes and improvements.
    An authentication screen has been added, which is useful if pyAggr3g470r
    is running on an EC2 instance, for example.

3.4 (2012-05-01)
----------------
    This version introduces some minor improvements and bugfixes.
    All features of pyAggr3g470r are now back (with MongoDB).

3.3 (2012-04-16)
----------------
    This version introduces minor improvements and a bugfix.
    Publication dates of articles are now stored as a datetime object.
    A bug in the script that converts an SQLite database to a MongoDB database
    is now fixed.
    A little documentation has been added.

3.2 (2012-03-20)
----------------
    A MongoDB database is now used instead of the SQLite database. This change
    offers a significant performance improvement. The database has been tested
    with more than 30,000 articles, but version 3.2 is still a test version.
    A more stable version will arrive soon.

3.1 (2011-11-29)
----------------
    A new version of the QR Code module is used. For each article, a QR Code
    is generated based on the content of the article. If the article is too
    long, only the article's URL is encoded in the QR Code. For a given
    string, the algorithm tries the generate as small a QR Code as possible.
    Minor bugs were fixed.

3.0 (2011-10-25)
----------------
    This release introduces exportation of articles to the HTML format and to
    the PDF format (there is still exportation to ePub).
    The sharing of articles with delicious.com was replaced by pinboard.in.s

2.9 (2011-08-26)
----------------
    Some minor improvements. A bug with the HTML <code> tag bas been fixed.
    Cleanup was done with Pylint.
    The test database of pyAggr3g470r contains more than 22000 articles,
    and it runs perfectly.

2.8 (2011-07-08)
----------------
    The feed summary page, which displays general information about a feed,
    now lets you change the feed metadata (feed logo, feed name, and feed URL
    if changed). Moreover, this page displays the activity of a feed and other
    useful information. It is now possible to set a different POD for Diaspora
    in the configuration file and to share an article with Google +1.
    A control file to start or stop pyAggr3g470r has been added.
    From the GUI side, a new transparent CSS tooltip has been introduced in
    order to preview an article.
    Finally, some minor performance improvements and bugfixes were made.

2.7 (2011-04-15)
----------------
    Minor improvements.
    It is now possible to set a maximum number of articles to be loaded from
    the database for each feed (via the management page).

2.6 (2011-03-21)
----------------
    This version introduces a new page that displays general information about
    a feed. There are some minor improvements in the Web interface.
    The version of pyAggr3g470r for Python 3 is now fully ready and has been
    tested with Python 3.2.

2.5 (2011-01-19)
----------------
    A bug when removing a feed from the data base was fixed.
    Minor improvements were made for export of articles and the size of HTML
    forms.

2.4 (2010-12-07)
----------------
    The GUI uses more HTML 5 features like HTML5 Forms Validation
    (email input, URL input), an HTML5 month+year date picker, and a
    placeholder. From each article it is possible to access the
    following and previous article (and a new main menu with CSS ToolTip).
    Articles can now be exported to the EPUB format. Articles loaded from the
    SQLite base are now stored in memory in a better data structure. With more
    than 10,000 articles, pyAggr3g470r starts in 3 seconds. Finally, email
    notifications are now sent with HTML message content and with an
    alternative plain text version (MIMEMultipart).

2.3 (2010-11-15)
----------------
    This version introduces HTML5 Forms Validation and a HTML5 month+year date
    picker for the history page, which can be used to search for articles.
    This currently only works with Opera.

2.2 (2010-11-03)
----------------
    There is now a third way to export articles from the SQLite base.
    There is an export method for the wiki DokuWiki (example in the commit
    message).

2.1 (2010-10-25)
----------------
    The export of articles to HTML has been updated, with better output.
    There are a number of improvements (the search function, generation of
    tags cloud, display of article content, CSS, bugfixes, etc.).
    There is a new Wiki.

2.0 (2010-09-03)
----------------
    It is now possible to browse articles by year and month with tag clouds
    (see new screenshots).
    In addition, URL errors are detected before downloading feeds.
    There are some improvements in the user interface.

1.9 (2010-09-02)
----------------
    The feedgetter module was improved. More details about articles are stored
    in the database when possile. An attempt is made to get the whole article
    (a_feed['entries'][i].content[j].value), and in the event of failure,
    the description/summary is used (a_feed['entries'][i].description).

1.8 (2010-08-25)
----------------
    It is now easier to install pyAggr3g470r.
    There is no longer any need to set any path in the configuration file.

1.7 (2010-07-23)
----------------
    This release generates QR codes with URLs of articles, so you can read an
    article later on your smartphone (or share with friends).

1.6 (2010-07-08)
----------------
    It is now possible to automatically add a feed (with the URL of the site),
    delete an article, delete a feed with all its articles, and to delete all
    articles from the database.
    There are also some nice improvements to performance, tested with more
    than 3000 articles.
    Furthermore, HTML export of all the articles of the database was improved.
    You can also export the articles in raw text. Finally, some minor bugs
    were fixed.

1.5 (2010-07-05)
----------------
    Now pyAggr3g470r only works with Python 2.7.
    OrderedDict objects are used in order to sort the feeds alphabetically in
    a simple way.

1.4 (2010-06-10)
----------------
    It is now possible to remove all articles of a given feed from the SQLite
    base via the management page. You can also add a feed just with the URL
    of the Web page. The URL of the feed is obtained by parsing the Web page
    with the module BeautifulSoup.

1.3 (2010-05-04)
----------------
    All articles stored in the SQLite database can now be exported as HTML or
    raw text via the management page.

1.2 (2010-04-29)
----------------
    This version introduces a tag cloud with variable word length.
    Some improvements were made to the CSS and a bug was fixed.

1.1 (2010-04-15)
----------------
    Introduction of a Google Buzz button.
    It is now possible to mark or unmark articles as favorites.

1.0 (2010-03-23)
----------------
    The database of feeds is monitored with the Python gamin module,
    if present. Otherwise it is done with a classic function.
    You now have the option to be informed of new articles by email. To
    receive these notifications, just click on "Stay tuned" for the
    desired feed(s) at the main page of pyAggr3g470r in the browser.

0.9 (2010-02-28)
----------------
    TuxDroid tells you when there are unread articles (this module is
    independent in case you don't have a TuxDroid). Moreover, the language of
    articles is detected (thanks to the oice.langdet Python module). This
    allows you to search for articles by language.

0.8 (2010-02-24)
----------------
    It is now possible to share articles with delicious, Digg, reddit,
    Scoopeo, and Blogmarks.
    The "Management of feeds" page presents information on the database and
    statistics on articles (with a histogram). HTML tags are now skipped for
    the search. Some other improvements were made.

0.7 (2010-02-15)
----------------
    It is now possible to search for an article, through the titles and
    descriptions.

0.6 (2010-02-05)
----------------
    Unread articles are now shown in bold. This was implemented using a new
    field in the SQLite database. New tabs for article descriptions are opened
    with the _rel=noreferrer_ option in order to separate processes (useful
    with Chromium). It is now possible to see only unread articles for each feed.

0.5 (2010-02-02)
----------------
    It is now possible to fetch feeds manually by clicking on "Fetch all feeds"
    and/or with cron. Better navigation between feeds and improvements to the
    SQLite database have been added.

0.4 (2010-02-01)
----------------
    Release 0.4. The main page display only 10 articles by feeds.
    For each feeds a page present the list of all articles. The SQLite base is
    smaller than before (removed hashed value).
    A lot of improvements.

0.3 (2010-02-01)
----------------
    A new menu was added for faster access to feeds. Some improvements were
    made to the CSS.

0.2 (2010-01-31)
----------------
    Articles are now sorted by date, and it is possible to read just a
    description of an article. There are some improvements in the code and
    SQLite base management.

0.1 (2010-01-29)
----------------
    First release of pyAggr3g470r.

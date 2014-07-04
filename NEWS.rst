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
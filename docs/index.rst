.. pyAggr3g470r documentation master file, created by
   sphinx-quickstart on Sat Sep 15 08:55:50 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyAggr3g470r's documentation!
========================================

.. toctree::
   :maxdepth: 2


Presentation
------------

pyAggr3g470r_ is a multi-threaded news aggregator with a web interface
based on CherryPy_. Articles are stored in a MongoDB_ base.



Features
--------

* articles are stored in a MongoDB_ database;
* find an article with history;
* e-mail notification;
* export articles to HTML, EPUB, PDF or raw text;
* mark or unmark articles as favorites;
* share articles with Diaspora, Google Buzz, Pinboard, delicious, Identi.ca, Digg, reddit, Scoopeo, Blogmarks and Twitter;
* generation of QR code with the content or URL of an article. So you can read an article later on your smartphone (or share with friends).


Installation
------------
Requierements
~~~~~~~~~~~~~
Software required
`````````````````

* Python_ 2.7.*;
* MongoDB_ and PyMongo_;
* feedparser_;
* CherryPy_ (version 3 and up);
* BeautifulSoup_.


Optional module
```````````````

These modules are not required but enables more features:
* lxml and Genshi;
* Python Imaging Library for the generation of QR codes.


If you want to install these modules:

.. code-block:: bash

    $ sudo aptitude install  python-lxml python-genshi


Setting
~~~~~~~

Rename the file **./cfg/pyAggr3g470r.cfg-sample** to **./cfg/pyAggr3g470r.cfg**.
By default you don't have to edit this file (only to configure mail notification).

Then, indicate the feeds to retrieve in the file **./var/feed.lst**. One feed per line. For example :

.. code-block:: cfg

    http://blog.cedricbonhomme.org/feed/
    http://linuxfr.org/backend/news-homepage/rss20.rss
    http://rss.slashdot.org/Slashdot/slashdot
    http://theinvisiblethings.blogspot.com/feeds/posts/default
    http://torvalds-family.blogspot.com/feeds/posts/default
    http://www.python.org/channews.rdf
    http://www.kde.org/dotkdeorg.rdf
    http://feeds.feedburner.com/internetactu/bcmJ
    http://www.april.org/fr/rss.xml
    http://www.framablog.org/index.php/feed/atom
    http://formats-ouverts.org/rss.php
    http://lwn.net/headlines/newrss
    http://kernelnewbies.org/RecentChanges?action=rss_rc&ddiffs=1&unique=1



Launch
------

Finally launch pyAggr3g470r in a shell:

.. code-block:: bash

    $ cd /home/cedric/pyaggr3g470r/
    $ pyAggr3g470r start



Backup
------

If you want to backup your database:

.. code-block:: bash

    $ su
    $ /etc/init.d/mongodb stop
    $ cp /var/lib/mongodb/pyaggr3g470r.* ~



Donnation
---------
If you wish and if you like pyAggr3g470r, you can donate via bitcoin. My bitcoin address: 1GVmhR9fbBeEh7rP1qNq76jWArDdDQ3otZ
Thank you!



License
-------
pyAggr3g470r_ is under GPLv3_ license.



Contact
-------

`My home page <http://cedricbonhomme.org/>`_.



.. _Python: http://python.org/
.. _pyAggr3g470r: https://bitbucket.org/cedricbonhomme/pyaggr3g470r/
.. _feedparser: http://feedparser.org/
.. _MongoDB: http://www.mongodb.org/
.. _PyMongo: https://github.com/mongodb/mongo-python-driver
.. _CherryPy: http://cherrypy.org/
.. _BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/
.. _GPLv3: http://www.gnu.org/licenses/gpl-3.0.txt

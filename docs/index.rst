.. pyAggr3g470r documentation master file, created by
   sphinx-quickstart on Sat Sep 15 08:55:50 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 2


Presentation
------------

pyAggr3g470r_ is a news aggregator with a web interface
based on CherryPy_. Articles are stored in a MongoDB_ base.

* `Ohloh page <http://www.ohloh.net/p/pyAggr3g470r>`_ of pyAggr3g470r;
* `Freecode page <http://freecode.com/projects/pyaggr3g470r>`_ of pyAggr3g470r.


Features
--------

* articles are stored in a MongoDB_ database (local or remote);
* article searching;
* e-mail notification;
* export articles to HTML, EPUB, PDF or raw text;
* favorite articles;
* language detection;
* sharing with Diaspora, Google Buzz, Pinboard, Identi.ca, Digg, reddit, Scoopeo, Blogmarks and Twitter;
* generation of QR codes with URLs of articles.


Installation
------------
Requierements
~~~~~~~~~~~~~
Software required
`````````````````

* Python_ >= 3.1;
* MongoDB_ and PyMongo_ >= 1.9;
* feedparser_ >= 5.1.2 (for **feedgetter.py**, the RSS feed parser);
* CherryPy_ >= 3.2.4 and Mako_ (for **pyAggr3g470r.py**, the Web interface);
* BeautifulSoup_ bs4 >= 4.1.2 (automatically find a feed in a HTML page).

Python 3.3 is recommend for better performances with large collections.

Optional module
```````````````

These modules are not required but enables more features:

* guess_language_ and PyEnchant_ for the language detection;
* lxml and Genshi for the generation of EPUB;
* Pillow (friendly fork of Python Imaging Library) for the generation of QR codes.


Script of installation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Installation of Python
    wget http://www.python.org/ftp/python/3.3.1/Python-3.3.1.tar.bz2
    tar -xvjf Python-3.3.1.tar.bz2
    rm Python-3.3.1.tar.bz2
    cd Python-3.3.1/
    ./configure
    make
    sudo make install
    cd ..
    sudo rm -Rf Python-3.3.1/
    # Installation of Distribute and PIP
    wget https://pypi.python.org/packages/source/d/distribute/distribute-0.6.36.tar.gz
    tar -xzvf distribute-0.6.36.tar.gz
    rm distribute-0.6.36.tar.gz
    cd distribute-0.6.36/
    sudo python3.3 setup.py install
    cd ..
    sudo rm -Rf distribute-0.6.36/
    wget https://github.com/pypa/pip/archive/develop.tar.gz -O pip-develop.tar.gz
    tar -xzvf pip-develop.tar.gz
    rm pip-develop.tar.gz
    cd pip-develop/
    sudo python3.3 setup.py install
    cd ..
    sudo rm -Rf pip-develop/
    # Core requirements for pyAggr3g470r
    sudo pip-3.3 install feedparser
    sudo pip-3.3 install beautifulsoup4
    sudo pip-3.3 install mako
    sudo pip-3.3 install pymongo
    # CherryPy, Minimalist Python Web Framework:
    wget  https://bitbucket.org/cherrypy/cherrypy/get/3.2.4.tar.gz
    tar -xzvf 3.2.4.tar.gz
    rm 3.2.4.tar.gz
    cd cherrypy-cherrypy-cd8acbc5f2b3/
    sudo python3.3 setup.py install
    cd ..
    sudo rm -Rf cherrypy-cherrypy-cd8acbc5f2b3/
    # Language detection:
    hg clone https://bitbucket.org/spirit/guess_language/
    cd guess_language/
    sudo python3.3 setup.py install
    cd ..
    sudo rm -Rf guess_language/
    # PyEnchant, for the language detection
    sudo pip-3.3 install pyenchant
    # Pillow, for the generation of QR Code
    sudo pip-3.3 install pillow
    # Finally, download pyAggr3g470r
    hg clone https://bitbucket.org/cedricbonhomme/pyaggr3g470r
    cd pyaggr3g470r/source/
    cp cfg/pyAggr3g470r.cfg-sample cfg/pyAggr3g470r.cfg
    exit 0


Setting
~~~~~~~

List of feeds
`````````````

Rename the file **./cfg/pyAggr3g470r.cfg-sample** to **./cfg/pyAggr3g470r.cfg**.
By default you don't have to edit this file (only in order to configure mail notification).

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


Create a new user
`````````````````
The default username is *admin* with the password *admin*. You can change the username and password
via the management page. Passwords are hashed and stored in the file **./var/password**.

Mail notification
`````````````````
If you wish to stay tuned from new articles of a feed by email, you have to edit the the **mail**
section of the configuration file:

* set the value of *enabled* to 1;
* set the *mail_to* value, your e-mail address (address of the recipient of the news);
* set the *smtp* value, the address of the SMTP server, and;
* set the *username* and *password* values for the authentication to the SMTP server.

.. code-block:: ini

    [MongoDB]
    address = 127.0.0.1
    port = 27017
    dbname = bob_pyaggr3g470r
    user = bob
    password =
    [mail]
    enabled = 0
    mail_from = pyAggr3g470r@no-reply.com
    mail_to = address_of_the_recipient@example.com
    smtp = smtp.example.com
    username = your_mail_address@example.com
    password = your_password
    [misc]
    diaspora_pod = joindiaspora.com

Then just click on "Stay tuned" for the desired feed(s) at the main page of pyAggr3g470r in your browser.


Launch
------
To launch pyAggr3g470r:

.. code-block:: bash

    $ cd ~/pyaggr3g470r/source/
    $ pyAggr3g470r start



Backup
------
If you want to backup your database:

.. code-block:: bash

    $ su
    $ /etc/init.d/mongodb stop
    $ cp /var/lib/mongodb/pyaggr3g470r.* ~

Alternatively you can use **mongodump**:

    $ mongodump --db pyaggr3g470r

And **mongorestore** to restore the database:

    $ mongorestore --db pyaggr3g470r dump/pyaggr3g470r/

**mongorestore** only performs inserts into the existing database.

Demo
----
* some `screen shots <https://plus.google.com/u/0/photos/106973022319954455496/albums/5449733578800221153>`_ of **pyAggr3g470r**;
* an old `video <http://youtu.be/Eyxpqn9Rpnw>`_ of pyAggr3g470r;
* an example of `HTML auto-generated archive <http://log.cedricbonhomme.org/>`_.



Donnation
---------
If you wish and if you like pyAggr3g470r, you can donate via bitcoin.

My bitcoin address: 1GVmhR9fbBeEh7rP1qNq76jWArDdDQ3otZ

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
.. _Mako: http://www.makotemplates.org/
.. _BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/
.. _guess_language: https://bitbucket.org/spirit/guess_language/
.. _PyEnchant: http://pypi.python.org/pypi/pyenchant
.. _GPLv3: http://www.gnu.org/licenses/gpl-3.0.txt

pyAggr3g470r
============

#### A simple Python news aggregator.


Presentation
------------
[pyAggr3g470r](https://bitbucket.org/cedricbonhomme/pyaggr3g470r/) is a news aggregator with a web interface
based on [Flask](http://flask.pocoo.org/). Articles are stored in a [MongoDB](http://api.mongodb.org/python/current/) base.


Features
------------
* articles are stored in a [MongoDB](http://www.mongodb.org/) database (local or remote);
* HTTP proxy support;
* fast full-text indexing and searching thanks the [Whoosh](https://bitbucket.org/mchaput/whoosh) library;
* e-mail notification;
* export articles to HTML, raw text;
* favorite articles;
* language detection;
* share articles with Diaspora, Google +, Pinboard, Identi.ca, Digg, reddit, Scoopeo, and Blogmarks.


Requierements
-------------

Software required

* [Python](http://python.org/) >= 3.1;
* [MongoDB](http://www.mongodb.org/) and [PyMongo](http://api.mongodb.org/python/current/) >= 1.9;
* [Whoosh](https://bitbucket.org/mchaput/whoosh) (article searching);
* [feedparser](http://code.google.com/p/feedparser/) >= 5.1.2 (for **feedgetter.py**, the RSS feed parser);
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) >= 4.1.2 (automatically find a feed in a HTML page).

Python 2.7.

Optional module

The module below is not required but enables more features:

* [guess_language](https://bitbucket.org/spirit/guess_language/) and [PyEnchant](http://pypi.python.org/pypi/pyenchant) for the language detection;


Backup
------

If you want to backup your database:

    $ su
    $ /etc/init.d/mongodb stop
    $ cp /var/lib/mongodb/pyaggr3g470r.* ~


Donation
--------
If you wish and if you like pyAggr3g470r, you can donate via bitcoin 1GVmhR9fbBeEh7rP1qNq76jWArDdDQ3otZ.
Thank you!


License
-------
[pyAggr3g470r](https://bitbucket.org/cedricbonhomme/pyaggr3g470r/) is under [GPLv3](http://www.gnu.org/licenses/gpl-3.0.txt) license.


Contact
-------
[My home page](http://cedricbonhomme.org/).

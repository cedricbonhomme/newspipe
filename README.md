pyAggr3g470r
============

#### A simple Python news aggregator.


Presentation
------------
[pyAggr3g470r](https://bitbucket.org/cedricbonhomme/pyaggr3g470r/) is a news aggregator with a web interface
based on [CherryPy](http://cherrypy.org/). Articles are stored in a [MongoDB](http://api.mongodb.org/python/current/) base.

A documentation is available [here](https://pyaggr3g470r.readthedocs.org/).


Features
------------
* articles are stored in a [MongoDB](http://www.mongodb.org/) database (local or remote);
* article searching;
* e-mail notification;
* export articles to HTML, EPUB, PDF or raw text;
* favorite articles;
* language detection;
* share articles with Diaspora, Google +, Pinboard, Identi.ca, Digg, reddit, Scoopeo, and Blogmarks;
* generation of QR codes with URLs of articles.


Requierements
-------------

Software required

* [Python](http://python.org/) >= 3.1;
* [MongoDB](http://www.mongodb.org/) and [PyMongo](http://api.mongodb.org/python/current/) >= 1.9;
* [feedparser](http://code.google.com/p/feedparser/) >= 5.1.2 (for **feedgetter.py**, the RSS feed parser);
* [CherryPy](http://cherrypy.org/) >= 3.2.2 and [Mako](http://www.makotemplates.org/) (for **pyAggr3g470r.py**, the Web interface);
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) >= 4.1.2 (automatically find a feed in a HTML page).

Python 3.3 is recommend for better performances with large collections.

Optional module

These modules are not required but enables more features:

* [guess_language](https://bitbucket.org/spirit/guess_language/) and [PyEnchant](http://pypi.python.org/pypi/pyenchant) for the language detection;
* lxml and Genshi;
* Python Imaging Library for the generation of QR codes.

Not yet tested with Python 3.3. Anyway, if you want to install these modules:

    $ sudo aptitude install python3.3-lxml python-genshi

Backup
------

If you want to backup your database:

    $ su
    $ /etc/init.d/mongodb stop
    $ cp /var/lib/mongodb/pyaggr3g470r.* ~


Donation
--------
If you wish and if you like pyAggr3g470r, you can donate via bitcoin. My bitcoin address: 1GVmhR9fbBeEh7rP1qNq76jWArDdDQ3otZ
Thank you!


License
-------
[pyAggr3g470r](https://bitbucket.org/cedricbonhomme/pyaggr3g470r/) is under [GPLv3](http://www.gnu.org/licenses/gpl-3.0.txt) license.


Contact
-------
[My home page](http://cedricbonhomme.org/).

pyAggr3g470r
============

#### A simple Python news aggregator.

Presentation
------------
pyAggr3g470r_ is a multi-threaded news aggregator with a web interface
based on CherryPy_. Articles are stored in a MongoDB_ base.



Features
------------
* articles are stored in a MongoDB_ database;
* find an article with history;
* e-mail notification;
* export articles to HTML, EPUB, PDF or raw text;
* mark or unmark articles as favorites;
* share articles with Diaspora, Google Buzz, Pinboard, delicious, Identi.ca, Digg, reddit, Scoopeo, Blogmarks and Twitter;
* generation of QR code with the content or URL of an article. So you can read an article later on your smartphone (or share with friends).



Requierements
-------------
Software required
~~~~~~~~~~~~~~~~~
* Python_ 2.7.*;
* MongoDB_ and PyMongo_;
* feedparser_;
* CherryPy_ (version 3 and up);
* BeautifulSoup_.


Optional module
~~~~~~~~~~~~~~~
These modules are not required but enables more features:
* lxml and Genshi;
* Python Imaging Library for the generation of QR codes.


If you want to install these modules:

    $ sudo aptitude install  python-lxml python-genshi


Backup
------

If you want to backup your database:

    $ su
    $ /etc/init.d/mongodb stop
    $ cp /var/lib/mongodb/pyaggr3g470r.* ~


Donnation
---------
If you wish and if you like pyAggr3g470r, you can donate via bitcoin. My bitcoin address: 1GVmhR9fbBeEh7rP1qNq76jWArDdDQ3otZ
Thank you!



License
------------
pyAggr3g470r_ is under GPLv3_ license.

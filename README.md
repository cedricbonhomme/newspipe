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
* share articles with Diaspora, Google +, Pinboard, Identi.ca, Digg, reddit, Scoopeo, and Blogmarks.


Requierements
-------------

Python >= 2.7.

To install the required libraries:

    $ sudo pip install --upgrade -r requirements.txt


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

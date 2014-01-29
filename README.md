pyAggr3g470r
============

#### A simple Python news aggregator.

Presentation
------------
[pyAggr3g470r](https://bitbucket.org/cedricbonhomme/pyaggr3g470r/) is a news aggregator with a web interface
based on [Flask](http://flask.pocoo.org/). Articles are stored in a [MongoDB](http://api.mongodb.org/python/current/) base.

Features
------------

* articles are stored in a [MongoDB](http://www.mongodb.org/) database;
* fast full-text indexing and searching thanks the [Whoosh](https://bitbucket.org/mchaput/whoosh) library;
* e-mail notification;
* export articles to HTML;
* favorite articles;
* share articles with Google +, Pinboard and reddit.

Some [screen shots](https://plus.google.com/u/0/photos/106973022319954455496/albums/5449733578800221153) of pyAggr3g470r.

Installation
------------

You need to have installed Python >= 2.7, MongoDB and some Python libraries.
Configuration is done via the file **conf/conf.cfg**.

Launch the script ``install.sh`` in order to install automatically all requirements.  
In order to prevent all dependencies problems and to keep your system stable, the libraries will be
installed in a Python virtual environment with ([virtualenv](http://www.virtualenv.org)).
The installation will use the configuration file for the database setup.

You can configure pyAggr3g470r (proxy, user agent, etc.) in the file ``conf/conf.cfg``.  
If you want to use pyAggr3g470r with Tor/Privoxy, you just have to set the value of
``http_proxy`` (for example: ``http_proxy = 127.0.0.1:8118``). Else leave the value blank.

Backup
------

If you want to backup your database:

    $ su
    $ /etc/init.d/mongodb stop
    $ cp /var/lib/mongodb/pyaggr3g470r.* ~

Donation
--------
If you wish and if you like pyAggr3g470r, you can donate via bitcoin
[1GVmhR9fbBeEh7rP1qNq76jWArDdDQ3otZ](https://blockexplorer.com/address/1GVmhR9fbBeEh7rP1qNq76jWArDdDQ3otZ).
Thank you!

License
-------
[pyAggr3g470r](https://bitbucket.org/cedricbonhomme/pyaggr3g470r/) is under [GPLv3](http://www.gnu.org/licenses/gpl-3.0.txt) license.

Contact
-------
[My home page](http://cedricbonhomme.org/).

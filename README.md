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
* favorite articles;
* share articles with Google +, Pinboard and reddit.

Some [screen shots](https://plus.google.com/u/0/photos/106973022319954455496/albums/5449733578800221153) of pyAggr3g470r.

Installation
------------

You need to have installed Python >= 2.7, MongoDB and some Python libraries.
Configuration is done via the file **conf/conf.cfg**.

    $ sudo apt-get install mongodb-server python-pip
    $ pip install --user virtualenv
    $ virtualenv --no-site-packages ./env_pyAggr3g470r
    $ source ./env_pyAggr3g470r/bin/activate
    $ pip install --upgrade -r requirements.txt
    $ cp conf/conf.cfg-sample conf/conf.cfg
    $ python initialization.py database_name firstname lastname email password
    $ python runserver.py

Alternatively you can run the script ``install.sh``.

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

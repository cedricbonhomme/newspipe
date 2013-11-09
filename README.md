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
* favorite articles;
* share articles with Google +, Pinboard and reddit.

Requierements
-------------

Python >= 2.7. To install the required libraries:

    $ sudo pip install --upgrade -r requirements.txt

Installation
------------

You can use the script initialization.py to create your user.

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

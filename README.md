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
Configuration is done via the file *conf/conf.cfg*.

Launch the script ``install.sh`` in order to install automatically all requirements.  
In order to prevent all dependencies problems and to keep your system stable, the libraries will be
installed in a Python virtual environment (with [virtualenv](http://www.virtualenv.org)).
The installation will use the configuration file for the database setup.

Then point your browser to the address [http://127.0.0.1:5000/](http://127.0.0.1:5000/) and login with the email address
*firstname.lastname@mail.com* and the password *secret*. You can update your profile at the
address [http://127.0.0.1:5000/profile/](http://127.0.0.1:5000/profile/).

As already said, you can configure pyAggr3g470r (database name, proxy, user agent, etc.) in the file *conf/conf.cfg*.  
For example if you want to use pyAggr3g470r with Tor/Privoxy, you just have to set the value of
*http_proxy* (most of the time: ``http_proxy = 127.0.0.1:8118``). Else leave the value blank.

However, the default configuration should be good, so you really just have to run the script *install.sh*.

Automatic updates
-----------------

You can fetch new articles with [cron](https://en.wikipedia.org/wiki/Cron) and the script *fetch.py*.
For example if you want to check for updates every 30 minutes, add this line to your cron rules (``crontab -e``):

    */30 * * * * cd ~/.pyaggr3g470r/ ; python fetch.py firstname.lastname@mail.com

You must give the email address you use to login to pyAggr3g470r.

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

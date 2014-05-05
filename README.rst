++++++++++++
pyAggr3g470r
++++++++++++

Presentation
============

`pyAggr3g470r <https://bitbucket.org/cedricbonhomme/pyaggr3g470r/>`_  is a news aggregator with a web interface
based on `Flask <http://flask.pocoo.org/>`_.

Features
========

* can be deployed on Heroku or on a traditional server;
* HTTP proxy support;
* feeds batch import with OPML files;
* export all your feeds to OPML;
* e-mail notification;
* export articles to HTML;
* favorite articles;
* share articles with Google +, Pinboard and reddit.


Usage
=====

Deployment
----------

This application can be deployed on Heroku or on a traditional server.

After installation, you will be able to connect with the email *root@pyAggr3g470r.localhost* and the password *root_password*.


Deploying the application on Heroku
'''''''''''''''''''''''''''''''''''

.. code:: bash

    $ git clone https://bitbucket.org/cedricbonhomme/pyaggr3g470r.git
    $ cd pyaggr3g470r
    $ heroku create
    $ heroku addons:add heroku-postgresql:dev
    $ heroku config:set HEROKU=1
    $ git push heroku master
    $ heroku run init
    $ heroku ps:scale web=1

An instance of pyAggr3g470r is running `here <https://pyaggr3g470r.herokuapp.com/>`_ .

Deploying the application on a traditional server
'''''''''''''''''''''''''''''''''''''''''''''''''

.. code:: bash

    $ git clone https://bitbucket.org/cedricbonhomme/pyaggr3g470r.git
    $ cd pyaggr3g470r
    $ sudo apt-get install libxml2-dev libxslt1-dev
    $ sudo pip install --upgrade -r requirements.txt
    $ cp conf/conf.cfg-sample conf/conf.cfg

If you want to use PostgreSQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    $ sudo apt-get install postgresql postgresql-server-dev-9.3 postgresql-client
    $ sudo -u postgres createuser
    Enter name of role to add: username
    Shall the new role be a superuser? (y/n) n
    Shall the new role be allowed to create databases? (y/n) y
    Shall the new role be allowed to create more new roles? (y/n) n
    $ createdb pyAggr3g470r
    $ sudo -u postgres psql
    postgres=# ALTER USER username WITH ENCRYPTED PASSWORD 'password';
    postgres=# GRANT ALL PRIVILEGES ON DATABASE pyAggr3g470r TO username;
    postgres=# \q

Edit the configuration file with the line:

.. code:: cfg

    [database]
    uri = postgres://username:password@127.0.0.1:5433/pyAggr3g470r

If you want to use SQLite
~~~~~~~~~~~~~~~~~~~~~~~~~

Just edit the configuration file with the line:

.. code:: cfg

    [database]
    uri = sqlite+pysqlite:///pyAggr3g470r.db


Finally:

.. code:: bash

    $ python db_create.py
    $ python runserver.py
     * Running on http://0.0.0.0:5000/
     * Restarting with reloader


Configuration
-------------

Configuration (database url, email, proxy, user agent, etc.) is done via the file *conf/conf.cfg*.
Check these configuration before executing *db_create.py*.   
If you want to use pyAggr3g470r with Tor/Privoxy, you just have to set the value of
*http_proxy* (most of the time: *http_proxy = 127.0.0.1:8118**). Else leave the value blank.


Automatic updates
-----------------

You can fetch new articles with `cron <https://en.wikipedia.org/wiki/Cron>`_  and the script *fetch.py*.
For example if you want to check for updates every 30 minutes, add this line to your cron rules (*crontab -e*):

.. code:: bash

    */30 * * * * cd ~/.pyaggr3g470r/ ; python fetch.py firstname.lastname@mail.com

You must give the email address you use to login to pyAggr3g470r.


Donation
========

If you wish and if you like *pyAggr3g470r*, you can donate via bitcoin
`1GVmhR9fbBeEh7rP1qNq76jWArDdDQ3otZ <https://blockexplorer.com/address/1GVmhR9fbBeEh7rP1qNq76jWArDdDQ3otZ>`_.
Thank you!

Internationalization
====================

pyAggr3g470r is translated into English and French.

License
=======

`pyAggr3g470r <https://bitbucket.org/cedricbonhomme/pyaggr3g470r>`_
is under the `GNU Affero General Public License version 3 <https://www.gnu.org/licenses/agpl-3.0.html>`_.


Contact
=======

`My home page <http://cedricbonhomme.org/>`_.

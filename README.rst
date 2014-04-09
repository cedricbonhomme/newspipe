++++++++++++
pyAggr3g470r
++++++++++++

Presentation
============

`pyAggr3g470r <https://bitbucket.org/cedricbonhomme/pyaggr3g470r/>`_  is a news aggregator with a web interface
based on `Flask <http://flask.pocoo.org/>`_.

Features
========

* can be deployed both on Heroku and on a traditional server;
*  HTTP proxy support;
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

This application can be deployed both on Heroku and on a traditional server.

After installation, you will be able to connect with the e-mail *root@pyAggr3g470r.localhost* and the password *root*.


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


Deploying the application on a traditional server
'''''''''''''''''''''''''''''''''''''''''''''''''

.. code:: bash

    $ git clone https://bitbucket.org/cedricbonhomme/pyaggr3g470r.git
    $ cd pyaggr3g470r
    $ sudo apt-get install postgresql postgresql-server-dev-9.1 postgresql-client
    $ sudo pip install --upgrade -r requirements.txt
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
    $ export DATABASE_URL="postgres://username:password@127.0.0.1:5432/pyAggr3g470r"
    $ cp conf/conf.cfg-sample conf/conf.cfg
    $ python db_create.py
    $ python runserver.py
     * Running on http://0.0.0.0:5000/
     * Restarting with reloader

Configuration (email, proxy, user agent, etc.) is done via the file *conf/conf.cfg*.
For example if you want to use pyAggr3g470r with Tor/Privoxy, you just have to set the value of
*http_proxy* (most of the time: ``http_proxy = 127.0.0.1:8118``). Else leave the value blank.



Automatic updates
-----------------

You can fetch new articles with [cron](https://en.wikipedia.org/wiki/Cron) and the script *fetch.py*.
For example if you want to check for updates every 30 minutes, add this line to your cron rules (``crontab -e``):

    */30 * * * * cd ~/.pyaggr3g470r/ ; python fetch.py firstname.lastname@mail.com

You must give the email address you use to login to pyAggr3g470r.

Donation
========

If you wish and if you like *pyAggr3g470r*, you can donate via bitcoin
`1GVmhR9fbBeEh7rP1qNq76jWArDdDQ3otZ <https://blockexplorer.com/address/1GVmhR9fbBeEh7rP1qNq76jWArDdDQ3otZ>`_.
Thank you!

License
=======

`pyAggr3g470r <https://bitbucket.org/cedricbonhomme/pyaggr3g470r>`_
is under the `GNU Affero General Public License version 3 <https://www.gnu.org/licenses/agpl-3.0.html>`_.

Contact
=======

`My home page <http://cedricbonhomme.org/>`_.

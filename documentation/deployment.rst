Deployment
==========

This application can be deployed on Heroku or on a traditional server.

After installation, you will be able to connect with the email *root@pyAggr3g470r.localhost* and the password *password*.

Deploying the application with Vagrant
--------------------------------------

Installation of VirtualBox and Vagrant

.. code-block:: bash

    $ sudo apt-get install virtualbox
    $ wget https://dl.bintray.com/mitchellh/vagrant/vagrant_1.6.5_x86_64.deb
    $ sudo dpkg -i vagrant_1.6.5_x86_64.deb

Deployment of pyAggr3g470r

.. code-block:: bash

    $ git clone https://bitbucket.org/cedricbonhomme/pyaggr3g470r.git
    $ cd pyaggr3g470r/vagrant/
    $ vagrant up

Once the VM configured, go to the address http://127.0.0.1:5000.

Deploying the application on Heroku
-----------------------------------

An instance of pyAggr3g470r is running `here <https://pyaggr3g470r.herokuapp.com>`_.

The geek way
''''''''''''

.. code-block:: bash

    $ git clone https://bitbucket.org/cedricbonhomme/pyaggr3g470r.git
    $ cd pyaggr3g470r
    $ heroku create
    $ heroku addons:add heroku-postgresql:dev
    $ heroku config:set HEROKU=1
    $ git push heroku master
    $ heroku run init
    $ heroku ps:scale web=1

To enable account creation for users, you have to set some environment variables:

.. code-block:: bash

    $ heroku config:set SELF_REGISTRATION=1
    $ heroku config:set PLATFORM_URL=<URL-of-your-platform>
    $ heroku config:set RECAPTCHA_PUBLIC_KEY=<your-recaptcha-public-key>
    $ heroku config:set RECAPTCHA_PRIVATE_KEY=<your-recaptcha-private-key>
    $ heroku config:set NOTIFICATION_EMAIL=<notification-email>
    $ heroku config:set POSTMARK_API_KEY=<your-postmark-api-key>
    $ heroku addons:add postmark:10k

`Postmark <https://postmarkapp.com/>`_ is used to send account confirmation links.

If you don't want to open your platform just set *SELF_REGISTRATION* to 0.
You will be still able to create accounts via the administration page.


The simple way
''''''''''''''

Alternatively, you can deploy your own copy of the app using this button:

.. image:: https://www.herokucdn.com/deploy/button.png
    :target: https://heroku.com/deploy?template=https://github.com/cedricbonhomme/pyAggr3g470r

You will be prompted to choose an email and a password for the administrator's account.
And some other optional environment variables, as previously presented.

Deploying the application on a traditional server
-------------------------------------------------

.. code-block:: bash

    $ sudo apt-get install python libpq-dev python-dev python-pip build-essential git
    $ sudo apt-get install libxml2-dev libxslt1-dev # for lxml
    $ git clone https://bitbucket.org/cedricbonhomme/pyaggr3g470r.git
    $ cd pyaggr3g470r
    $ sudo pip install --upgrade -r requirements.txt
    $ cp conf/conf.cfg-sample conf/conf.cfg

If you want to use PostgreSQL
'''''''''''''''''''''''''''''

.. code-block:: bash

    $ sudo apt-get install postgresql postgresql-server-dev-9.3 postgresql-client
    $ pip install psycopg2
    $ echo "127.0.0.1:5432:aggregator:pgsqluser:pgsqlpwd" > ~/.pgpass
    $ chmod 700 ~/.pgpass
    $ sudo -u postgres createuser pgsqluser --no-superuser --createdb --no-createrole
    $ createdb aggregator --no-password
    $ echo "ALTER USER pgsqluser WITH ENCRYPTED PASSWORD 'pgsqlpwd';" | sudo -u postgres psql
    $ echo "GRANT ALL PRIVILEGES ON DATABASE aggregator TO pgsqluser;" | sudo -u postgres psql

Edit the configuration file with the line:

.. code-block:: cfg

    [database]
    uri = postgres://pgsqluser:pgsqlpwd@127.0.0.1:5433/aggregator

If you want to use SQLite
'''''''''''''''''''''''''

Just edit the configuration file with the line:

.. code-block:: cfg

    [database]
    uri = sqlite+pysqlite:///pyAggr3g470r.db


Finally:

.. code-block:: bash

    $ python manager.py db_create
    $ python runserver.py
     * Running on http://0.0.0.0:5000/
     * Restarting with reloader


Configuration
=============

Configuration (database url, email, proxy, user agent, etc.) is done via the file *conf/conf.cfg*.
Check these configuration before executing *db_create.py*.
If you want to use pyAggr3g470r with Tor/Privoxy, you just have to set the value of
*http_proxy* (most of the time: *http_proxy = 127.0.0.1:8118**). Else leave the value blank.


Automatic updates
=================

You can fetch new articles with `cron <https://en.wikipedia.org/wiki/Cron>`_  and the script *fetch.py*.
For example if you want to check for updates every 30 minutes, add this line to your cron rules (*crontab -e*):

.. code-block:: bash

    */30 * * * * cd ~/.pyaggr3g470r/ ; python manager.py fetch_asyncio None None

You must give the email address you use to login to pyAggr3g470r.

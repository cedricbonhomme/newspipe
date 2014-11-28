++++++++++++
pyAggr3g470r
++++++++++++

Presentation
============

`pyAggr3g470r <https://bitbucket.org/cedricbonhomme/pyaggr3g470r>`_  is a news aggregator with a web interface
based on `Flask <http://flask.pocoo.org>`_.

Features
========

* can be deployed on Heroku or on a traditional server;
* multiple users can use the platform;
* a RESTful API to manage your articles;
* data liberation: export and import all your account with a JSON file;
* export and import feeds with OPML files;
* export articles to HTML;
* e-mail notification;
* favorite articles;
* detection of inactive feeds;
* share articles with Google +, Pinboard and reddit;
* HTTP proxy support.


Usage
=====

Deployment
----------

This application can be deployed on Heroku or on a traditional server.

After installation, you will be able to connect with the email *root@pyAggr3g470r.localhost* and the password *password*.

Deploying the application with Vagrant
''''''''''''''''''''''''''''''''''''''

Installation of VirtualBox and Vagrant

.. code:: bash

    $ sudo apt-get install virtualbox
    $ wget https://dl.bintray.com/mitchellh/vagrant/vagrant_1.6.3_x86_64.deb
    $ sudo dpkg -i vagrant_1.6.3_x86_64.deb

Deployment of pyAggr3g470r

.. code:: bash

    $ git clone https://bitbucket.org/cedricbonhomme/pyaggr3g470r.git
    $ cd pyaggr3g470r/vagrant/
    $ vagrant up

Once the VM configured, go to the address http://127.0.0.1:5000.

Deploying the application on Heroku
'''''''''''''''''''''''''''''''''''

An instance of pyAggr3g470r is running `here <https://pyaggr3g470r.herokuapp.com>`_.

The geek way
~~~~~~~~~~~~

.. code:: bash

    $ git clone https://bitbucket.org/cedricbonhomme/pyaggr3g470r.git
    $ cd pyaggr3g470r
    $ heroku create
    $ heroku addons:add heroku-postgresql:dev
    $ heroku config:set BUILDPACK_URL=https://github.com/cedricbonhomme/heroku-buildpack-scipy
    $ heroku config:set HEROKU=1
    $ git push heroku master
    $ heroku run init
    $ heroku ps:scale web=1

To enable account creation for users, you have to set some environment variables:

.. code:: bash

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
~~~~~~~~~~~~~~

Alternatively, you can deploy your own copy of the app using this button:

.. image:: https://www.herokucdn.com/deploy/button.png
    :target: https://heroku.com/deploy?template=https://github.com/cedricbonhomme/pyAggr3g470r

You will be prompted to choose an email and a password for the administrator's account.
And some other optional environment variables, as previously presented.

Deploying the application on a traditional server
'''''''''''''''''''''''''''''''''''''''''''''''''

.. code:: bash

    $ sudo apt-get install python libpq-dev python-dev python-pip build-essential git
    $ sudo apt-get install libatlas-base-dev gfortran # for scipy
    $ sudo apt-get install libxml2-dev libxslt1-dev # for lxml
    $ sudo apt-get install python-nose # for scikit-learn
    $ git clone https://bitbucket.org/cedricbonhomme/pyaggr3g470r.git
    $ cd pyaggr3g470r
    $ sudo pip install --upgrade -r requirements.txt
    $ cp conf/conf.cfg-sample conf/conf.cfg

If you want to use PostgreSQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    $ sudo apt-get install postgresql postgresql-server-dev-9.3 postgresql-client
    $ echo "127.0.0.1:5432:aggregator:pgsqluser:pgsqlpwd" > ~/.pgpass
    $ chmod 700 ~/.pgpass
    $ sudo -u postgres createuser pgsqluser --no-superuser --createdb --no-createrole
    $ createdb aggregator --no-password
    $ echo "ALTER USER pgsqluser WITH ENCRYPTED PASSWORD 'pgsqlpwd';" | sudo -u postgres psql
    $ echo "GRANT ALL PRIVILEGES ON DATABASE aggregator TO pgsqluser;" | sudo -u postgres psql

Edit the configuration file with the line:

.. code:: cfg

    [database]
    uri = postgres://pgsqluser:pgsqlpwd@127.0.0.1:5433/aggregator

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


Web service
-----------

Articles
''''''''

.. code:: python

    >>> import requests, json
    >>> r = requests.get("https://pyaggr3g470r.herokuapp.com/api/v1.0/articles", auth=("your-email", "your-password"))
    >>> r.status_code
    200
    >>> rjson = json.loads(r.text)
    >>> rjson["result"][0]["title"]
    u'Sponsors required for KDE code sprint in Randa'
    >>> rjson["result"][0]["date"]
    u'Wed, 18 Jun 2014 14:25:18 GMT'

Possible parameters:

.. code:: bash

    $ curl --user your-email:your-password "https://pyaggr3g470r.herokuapp.com/api/v1.0/articles?filter_=unread&feed=24"
    $ curl --user your-email:your-password "https://pyaggr3g470r.herokuapp.com/api/v1.0/articles?filter_=read&feed=24&limit=20"
    $ curl --user your-email:your-password "https://pyaggr3g470r.herokuapp.com/api/v1.0/articles?filter_=all&feed=24&limit=20"

Get an article:

.. code:: bash

    $ curl --user your-email:your-password "https://pyaggr3g470r.herokuapp.com/api/v1.0/articles/84566"

Add an article:

.. code:: python

    >>> import requests, json
    >>> headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    >>> payload = {'link': 'http://blog.cedricbonhomme.org/2014/05/24/sortie-de-pyaggr3g470r-5-3/', 'title': 'Sortie de pyAggr3g470r 5.3', 'content':'La page principale de pyAggr3g470r a été améliorée...', 'date':'06/23/2014 11:42 AM', 'feed_id':'42'}
    >>> r = requests.post("https://pyaggr3g470r.herokuapp.com/api/v1.0/articles", headers=headers, auth=("your-email", "your-password"), data=json.dumps(payload))
    >>> print r.content
    {
        "message": "ok"
    }
    >>> r = requests.get("https://pyaggr3g470r.herokuapp.com/api/v1.0/articles?feed=42&limit=1", auth=("your-email", "your-password"))
    >>> print json.loads(r.content)["result"][0]["title"]
    Sortie de pyAggr3g470r 5.3

Update an article:

.. code:: python

    >>> payload = {"like":True, "readed":False}
    >>> r = requests.put("https://pyaggr3g470r.herokuapp.com/api/v1.0/articles/65", headers=headers, auth=("your-email", "your-password"), data=json.dumps(payload))
    >>> print r.content
    {
        "message": "ok"
    }

Delete an article:

.. code:: python

    >>> r = requests.delete("https://pyaggr3g470r.herokuapp.com/api/v1.0/articles/84574", auth=("your-email", "your-password"))
    >>> print r.status_code
    200
    >>> print r.content
    {
        "message": "ok"
    }
    >>> r = requests.delete("https://pyaggr3g470r.herokuapp.com/api/v1.0/articles/84574", auth=("your-email", "your-password"))
    >>> print r.status_code
    200
    >>> print r.content
    {
        "message": "Article not found."
    }

Feeds
'''''

Add a feed:

.. code:: python

    >>> payload = {'link': 'http://blog.cedricbonhomme.org/feed'}
    >>> r = requests.post("https://pyaggr3g470r.herokuapp.com/api/v1.0/feeds", headers=headers, auth=("your-email", "your-password"), data=json.dumps(payload))

Update a feed:

.. code:: python

    >>> payload = {"title":"Feed new title", "description":"New description"}
    >>> r = requests.put("https://pyaggr3g470r.herokuapp.com/api/v1.0/feeds/42", headers=headers, auth=("your-email", "your-password"), data=json.dumps(payload))

Delete a feed:

.. code:: python

    >>> r = requests.delete("https://pyaggr3g470r.herokuapp.com/api/v1.0/feeds/29", auth=("your-email", "your-password"))

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

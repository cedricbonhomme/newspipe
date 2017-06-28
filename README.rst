=============
🗞 Newspipe 🗞
=============

Presentation
------------

`Newspipe <https://github.com/newspipe/newspipe>`_ is a web-based news
aggregator and reader.

Main features
-------------

* can be easily deployed on Heroku or on a traditional server;
* multiple users can use a Newspipe instance;
* a RESTful API to manage your articles (or connect your own crawler);
* data liberation: export and import all your account with a JSON file;
* export and import feeds with OPML files;
* favorite articles;
* detection of inactive feeds;
* share articles with Google +, Pinboard and reddit;
* personal management of bookmarks (with import from Pinboard).

The core technologies are `Flask <http://flask.pocoo.org>`_,
`asyncio <https://www.python.org/dev/peps/pep-3156/>`_ ,
`SQLAlchemy <http://www.sqlalchemy.org>`_
and `React <https://facebook.github.io/react/>`_.

Python >= 3.5 is required.

Documentation
-------------

A documentation is available `here <https://newspipe.readthedocs.io>`_ and
provides different ways to
`install Newspipe <https://newspipe.readthedocs.io/en/latest/deployment.html>`_.

Test Newspipe on Heroku:

.. image:: https://www.herokucdn.com/deploy/button.png
    :target: https://heroku.com/deploy?template=https://github.com/newspipe/newspipe.git

It is important to specify an application name and the URL of your instance
(*PLATFORM_URL*) through the Heroku form.

Contributions
-------------

Contributions are welcome. If you want to contribute to Newspipe I highly
recommend you to install it in a Python virtual environment. For example:


.. code-block:: bash

    git clone https://github.com/newspipe/newspipe.git
    cd newspipe/
    pew install 3.6.1 --type CPython
    pew new --python=$(pew locate_python 3.6.1)  -a . -r requirements.txt newspipe-dev
    cp src/conf/conf.cfg-sample src/conf/conf.cfg
    python src/manager.py db_create
    npm install
    python src/runserver.py
      * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)

License
-------

`Newspipe <https://github.com/newspipe/newspipe>`_ is under the
`GNU Affero General Public License version 3 <https://www.gnu.org/licenses/agpl-3.0.html>`_.

Contact
-------

`Cédric Bonhomme <https://www.cedricbonhomme.org>`_

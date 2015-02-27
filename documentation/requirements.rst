Requirements
============

The complete list of required Python modules is in the file
``requirements.txt``.

The core technologies used are:

* `Flask <http://flask.pocoo.org>`_ for the web backend;
* `asyncio <https://www.python.org/dev/peps/pep-3156/>`_ for the crawler;
* `SQLAlchemy <http://www.sqlalchemy.org>`_ for the data base.

Python 3.4 is highly recommended, especially for the feed crawler.
The web server is working with Python 2.7 and Python 3.

It is possible to connect your own crawler to the RESTful API.

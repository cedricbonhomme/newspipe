# Newspipe

[![builds.sr.ht status](https://builds.sr.ht/~cedric/newspipe.svg)](https://builds.sr.ht/~cedric/newspipe)

## Presentation

[Newspipe](https://github.com/cedricbonhomme/newspipe) is a web news aggregator.

![Newspipe Home page](docs/static/newspipe_home-page.png "Newspipe Home page")

Newspipe is written in Python. The core technologies are
[Flask](http://flask.pocoo.org),
[asyncio](https://www.python.org/dev/peps/pep-3156/) and
[SQLAlchemy](http://www.sqlalchemy.org).


## Main features

* multiple users can use a Newspipe instance;
* an API to manage feeds (you can connect your own crawler);
* data liberation: export and import your account with a JSON file;
* export and import feeds with OPML files;
* search and favorite articles;
* detection of inactive feeds;
* management of bookmarks (with import from Pinboard).
* Optional ldap authentication


## Deployment

Newspipe is really easy to deploy.

Assuming you have already installed ``git``, ``poetry``, ``npm``,  and
``Python >= 3.10``, you just have to do the following:

```bash
$ git clone https://github.com/cedricbonhomme/newspipe
$ cd newspipe/
$ npm ci
$ poetry install --no-dev
$ poetry shell
$ pybabel compile -d newspipe/translations
$ export NEWSPIPE_CONFIG=sqlite.py
$ export FLASK_APP=runserver.py
$ export FLASK_DEBUG=1
$ flask db_create
$ flask db_init
$ flask create_admin --nickname <nickname> --password <password>
$ flask run
 * Serving Flask app "runserver" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 221-873-938
```

If you want to use PostgreSQL you can customize
the provided example configuration file (``instance/config.py``):

```bash
$ sudo apt-get install postgresql
$ cp instance/config.py instance/postgresql.py
$ vim instance/postgresql.py # customize it
$ export NEWSPIPE_CONFIG=postgresql.py
```

For production you can use [Gunicorn](https://gunicorn.org) or ``mod_wsgi``.


## License

[Newspipe](https://github.com/cedricbonhomme/newspipe) is under the
[GNU Affero General Public License version 3](https://www.gnu.org/licenses/agpl-3.0.html).


## Contact

[Cédric Bonhomme](https://www.cedricbonhomme.org)

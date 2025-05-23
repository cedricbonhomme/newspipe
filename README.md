# Newspipe

## Presentation

[Newspipe](https://github.com/cedricbonhomme/newspipe) is a web news aggregator.

![Newspipe Home page](docs/static/newspipe_home-page.png "Newspipe Home page")

Newspipe is written in Python. The core technologies are
[Flask](http://flask.pocoo.org),
[asyncio](https://www.python.org/dev/peps/pep-3156/) and
[SQLAlchemy](http://www.sqlalchemy.org).


## Main features

* multiple users can use a Newspipe instance
* an API to manage feeds (you can connect your own crawler)
* data liberation: export and import your account with a JSON file
* export and import feeds with OPML files
* search and favorite articles
* detection of inactive feeds
* management of bookmarks (with import from Pinboard)
* optional ldap authentication (see the example configuration file)
* user interface available with a light theme and a dark theme


## Deployment

Newspipe is really easy to deploy.
Assuming you have already installed ``git``, ``poetry``, ``npm``,  and
``Python >= 3.10``, you just have to do the following:

```bash
$ git clone https://github.com/cedricbonhomme/newspipe
$ cd newspipe/
$ npm ci
$ poetry install
$ poetry shell
$ pybabel compile -d newspipe/translations
$ export NEWSPIPE_CONFIG=sqlite.py
$ flask db_init
$ flask create_admin --nickname <nickname> --password <password>
$ flask run --debug
 * Debug mode: on
```

If you want to use PostgreSQL you can customize
the provided example configuration file (``instance/config.py``):

```bash
$ sudo apt-get install postgresql
$ cp instance/config.py instance/postgresql.py
$ vim instance/postgresql.py # customize it
$ export NEWSPIPE_CONFIG=postgresql.py
$ flask db_create
$ flask db_init
...
```

For production you can use [Gunicorn](https://gunicorn.org) or ``mod_wsgi``.

### Updates and migrations

```bash
$ cd newspipe/
$ git pull origin master
$ poetry install
$ poetry run flask db upgrade
$ poetry run pybabel compile -d newspipe/translations
```

## Retrieving feeds automatically

A dedicated Flask command is available to run the RSS/Atom feed importer.
You can schedule it using a cron job, for example:

```bash
0 */3 * * * poetry run flask fetch_asyncio
```

When using cron it is usally best to be more precise with the command location, for example:

```bash
0 */3 * * * FLASK_APP=app.py /home/cedric/.cache/pypoetry/virtualenvs/newspipe-19mdZ4UL-py3.12/bin/flask fetch_asyncio
```

## License

[Newspipe](https://github.com/cedricbonhomme/newspipe) is under the
[GNU Affero General Public License version 3](https://www.gnu.org/licenses/agpl-3.0.html).


## Donations

If you wish and if you like Newspipe, you can donate:

[![GitHub Sponsors](https://img.shields.io/github/sponsors/cedricbonhomme)](https://github.com/sponsors/cedricbonhomme)

or with Bitcoin to this address:
bc1q56u6sj7cvlwu58v5lemljcvkh7v2gc3tv8mj0e

Thank you !


## Contact

[Cédric Bonhomme](https://www.cedricbonhomme.org)

# Newspipe

[![builds.sr.ht status](https://builds.sr.ht/~cedric/newspipe.svg)](https://builds.sr.ht/~cedric/newspipe)

## Presentation

[Newspipe](https://git.sr.ht/~cedric/newspipe) is a web news aggregator.

Newspipe is written in Python. The core technologies are
[Flask](http://flask.pocoo.org),
[asyncio](https://www.python.org/dev/peps/pep-3156/) and
[SQLAlchemy](http://www.sqlalchemy.org).

For reporting issues, visit the tracker here:
https://todo.sr.ht/~cedric/newspipe

For contributions, use the mailing list to send your patches:
https://lists.sr.ht/~cedric/newspipe


## Main features

* multiple users can use a Newspipe instance;
* an API to manage feeds (you can connect your own crawler);
* data liberation: export and import your account with a JSON file;
* export and import feeds with OPML files;
* search and favorite articles;
* detection of inactive feeds;
* share articles on Pinboard, Reddit and Twitter;
* management of bookmarks (with import from Pinboard).


## Deployment

Newspipe is really easy to deploy.

### Requirements

```bash
$ sudo apt-get install npm postgresql
```

##  Configure and install the application

```bash
$ git clone https://git.sr.ht/~cedric/newspipe
$ cd newspipe/
$ npm install
$ poetry install
$ cp instance/production.py instance/development.py
$ poetry shell
$ python manager.py db_create
$ python runserver.py
  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

If you want to use SQLite you do not need to install PostgreSQL. Simply use
the provided configuration file (in ``instance/sqlite.py``) thank to this
environment variable:

```bash
export Newspipe_CONFIG=sqlite.py
```

## License

[Newspipe](https://git.sr.ht/~cedric/newspipe) is under the
[GNU Affero General Public License version 3](https://www.gnu.org/licenses/agpl-3.0.html).


## Contact

[Cédric Bonhomme](https://www.cedricbonhomme.org)

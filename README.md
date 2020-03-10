# Newspipe

## Presentation

[Newspipe](https://git.sr.ht/~cedric/newspipe) is a web-based news
aggregator and reader.

For reporting issues, visit the tracker here:
https://todo.sr.ht/~cedric/newspipe

For contributions, use the mailing list to send your patches:
https://lists.sr.ht/~cedric/newspipe

Newspipe is written in Python. The core technologies are
[Flask](http://flask.pocoo.org),
[asyncio](https://www.python.org/dev/peps/pep-3156/) and
[SQLAlchemy](http://www.sqlalchemy.org).


## Main features

* multiple users can use a Newspipe instance;
* an API to manage your feeds (you can connect your own crawler);
* data liberation: export and import your account with a JSON file;
* export and import feeds with OPML files;
* search and favorite articles;
* detection of inactive feeds;
* share on Pinboard and reddit;
* management of bookmarks (with import from Pinboard).


## Deployment

Newspipe is really easy to deploy.

### Requirements

```bash
$ sudo apt-get install postgresql npm
```

##  Configure and install the application

```bash
$ git clone https://git.sr.ht/~cedric/newspipe
$ cd newspipe/
$ poetry install
$ npm install
$ cp instance/production.py instance/development.py
$ poetry shell
$ python manager.py db_create
$ python runserver.py
  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

## License

[Newspipe](https://git.sr.ht/~cedric/newspipe) is under the
[GNU Affero General Public License version 3](https://www.gnu.org/licenses/agpl-3.0.html).


## Contact

[Cédric Bonhomme](https://www.cedricbonhomme.org)

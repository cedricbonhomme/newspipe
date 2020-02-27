# Newspipe

## Presentation

[Newspipe](https://git.sr.ht/~cedric/newspipe) is a web-based news
aggregator and reader.

For reporting issues, visit the tracker here:
https://todo.sr.ht/~cedric/newspipe

For contributions the list is here:
https://lists.sr.ht/~cedric/newspipe

## Main features

* easy to deploy;
* multiple users can use a Newspipe instance;
* a RESTful API to manage your articles (or connect your own crawler);
* data liberation: export and import all your account with a JSON file;
* export and import feeds with OPML files;
* favorite articles;
* detection of inactive feeds;
* share on Pinboard and reddit;
* personal management of bookmarks (with import from Pinboard).

The core technologies are [Flask](http://flask.pocoo.org),
[asyncio](https://www.python.org/dev/peps/pep-3156/),
[SQLAlchemy](http://www.sqlalchemy.org).


## Deployment

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
$ cp newspipe/conf/conf.cfg-sample newspipe/conf/conf.cfg
$ poetry shell
$ python newspipe/manager.py db_create
$ python newspipe/runserver.py
  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

## License

[Newspipe](https://git.sr.ht/~cedric/newspipe) is under the
[GNU Affero General Public License version 3](https://www.gnu.org/licenses/agpl-3.0.html).


## Contact

[Cédric Bonhomme](https://www.cedricbonhomme.org)

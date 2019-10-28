# Newspipe

## Presentation

[Newspipe](https://git.sr.ht/~cedric/Newspipe) is a web-based news
aggregator and reader.

## Main features

* can be easily deployed on Heroku or on your server;
* multiple users can use a Newspipe instance;
* a RESTful API to manage your articles (or connect your own crawler);
* data liberation: export and import all your account with a JSON file;
* export and import feeds with OPML files;
* favorite articles;
* detection of inactive feeds;
* Pinboard and reddit;
* personal management of bookmarks (with import from Pinboard).

The core technologies are [Flask](http://flask.pocoo.org),
[asyncio](https://www.python.org/dev/peps/pep-3156/),
[SQLAlchemy](http://www.sqlalchemy.org)
and [React](https://facebook.github.io/react/).


## Documentation

A documentation is available [here](https://newspipe.readthedocs.io) and
provides different ways to
[install Newspipe](https://newspipe.readthedocs.io/en/latest/deployment.html).

Test Newspipe on Heroku:

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://builds.sr.ht/~cedric/Stegano)

It is important to specify an application name and the URL of your instance
(*PLATFORM_URL*) through the Heroku form.


## Deployment

### Requirements

```bash
$ sudo apt-get install postgresql npm
```

##  Configure and install the application

```bash
$ git clone https://git.sr.ht/~cedric/Newspipe
$ cd newspipe/
$ pipenv install
✨🍰✨
$ npm install
$ cp src/conf/conf.cfg-sample src/conf/conf.cfg
$ pipenv shell
$ python src/manager.py db_create
$ python src/runserver.py
  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

## License

[Newspipe](https://git.sr.ht/~cedric/Newspipe) is under the
[GNU Affero General Public License version 3](https://www.gnu.org/licenses/agpl-3.0.html).


## Contact

[Cédric Bonhomme](https://www.cedricbonhomme.org)

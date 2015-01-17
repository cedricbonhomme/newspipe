#!/usr/bin/env python
from bootstrap import application, db
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand


Migrate(application, db)

manager = Manager(application)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()

#!/usr/bin/env python
import os
from bootstrap import application, db, populate_g
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from werkzeug import generate_password_hash

from sqlalchemy.engine import reflection
from sqlalchemy.schema import (
        MetaData,
        Table,
        DropTable,
        ForeignKeyConstraint,
        DropConstraint)


Migrate(application, db)

manager = Manager(application)
manager.add_command('db', MigrateCommand)

@manager.command
def db_empty():
    "Will drop every datas stocked in db."
    # From http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything
    conn = db.engine.connect()

    # the transaction only applies if the DB supports
    # transactional DDL, i.e. Postgresql, MS SQL Server
    trans = conn.begin()

    inspector = reflection.Inspector.from_engine(db.engine)

    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in
    # a transaction.
    metadata = MetaData()

    tbs = []
    all_fks = []

    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(ForeignKeyConstraint((), (), name=fk['name']))
        t = Table(table_name, metadata, *fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        conn.execute(DropConstraint(fkc))

    for table in tbs:
        conn.execute(DropTable(table))

    trans.commit()

@manager.command
def db_create():
    "Will create the database from conf parameters."
    with application.app_context():
        populate_g()
        from pyaggr3g470r.models import User, Role
        db.create_all()

        role_admin = Role(name="admin")
        role_user = Role(name="user")

        user1 = User(nickname="admin",
                    email=os.environ.get("ADMIN_EMAIL",
                                        "root@pyAggr3g470r.localhost"),
                    pwdhash=generate_password_hash(
                            os.environ.get("ADMIN_PASSWORD", "password")),
                    activation_key="")
        user1.roles.extend([role_admin, role_user])

        db.session.add(user1)
        db.session.commit()

@manager.command
def fetch(user, password, limit=10):
    "Crawl the feeds with the client crawler."
    from pyaggr3g470r.lib.crawler import CrawlerScheduler
    scheduler = CrawlerScheduler(user, password)
    scheduler.run(limit=limit)
    scheduler.wait()

@manager.command
def fetch_asyncio(user_id, feed_id):
    "Crawl the feeds with asyncio."
    with application.app_context():
        populate_g()
        from pyaggr3g470r.models import User
        from pyaggr3g470r import crawler
    users, feed_id = [], None
    try:
        users = User.query.filter(User.id == int(user_id)).all()
    except:
        users = User.query.all()
    finally:
        if users == []:
            users = User.query.all()

    try:
        feed_id = int(feed_id)
    except:
        feed_id = None

    for user in users:
        if user.activation_key == "":
            print("Fetching articles for " + user.nickname)
            feed_getter = crawler.retrieve_feed(user, feed_id)


if __name__ == '__main__':
    manager.run()

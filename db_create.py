#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.2 $"
__date__ = "$Date: 2014/03/16 $"
__revision__ = "$Date: 2014/03/24 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "AGPLv3"

from pyaggr3g470r import db
from pyaggr3g470r.models import User, Feed, Role
from werkzeug import generate_password_hash

from sqlalchemy.engine import reflection
from sqlalchemy.schema import (
        MetaData,
        Table,
        DropTable,
        ForeignKeyConstraint,
        DropConstraint,
        )

def db_DropEverything(db):
    # From http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything

    conn=db.engine.connect()

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
            fks.append(
                ForeignKeyConstraint((),(),name=fk['name'])
                )
        t = Table(table_name,metadata,*fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        conn.execute(DropConstraint(fkc))

    for table in tbs:
        conn.execute(DropTable(table))

    trans.commit()



db_DropEverything(db)
db.create_all()

role_admin = Role(name="admin")
role_user = Role(name="user")

user1 = User(firstname="admin", lastname="admin", email="root@pyAggr3g470r.localhost", pwdhash=generate_password_hash("root"))

user1.roles.extend([role_admin, role_user])

feed1 = Feed(title="Armed and Dangerous", description="Sex, software, politics, and firearms. Life's simple pleasures...",
             link="http://esr.ibiblio.org/?feed=rss2", site_link="http://esr.ibiblio.org/",
             email_notification=False, enabled=True, user_id=user1.id)

user1.feeds.extend([feed1])

db.session.add(user1)
db.session.commit()
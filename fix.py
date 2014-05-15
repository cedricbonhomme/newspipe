#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.3 $"
__date__ = "$Date: 2014/03/16 $"
__revision__ = "$Date: 2014/04/12 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "AGPLv3"

from pyaggr3g470r import db
from pyaggr3g470r.models import User, Role
from werkzeug import generate_password_hash

from sqlalchemy.engine import reflection
from sqlalchemy.schema import (
        MetaData,
        Table,
        DropTable,
        ForeignKeyConstraint,
        DropConstraint,
        )


role_admin = Role.query.filter(Role.name == "admin").first()
user = User.query.filter(User.email == "kimble.mandel@gmail.com").first()
user.roles = [role_admin]
db.session.commit()
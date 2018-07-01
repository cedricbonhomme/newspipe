#! /usr/bin/env python
# -*- coding: utf-8 -*-

# newspipe - A Web based news aggregator.
# Copyright (C) 2010-2018  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : https://github.com/Newspipe/Newspipe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.4 $"
__date__ = "$Date: 2013/11/05 $"
__revision__ = "$Date: 2014/04/12 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

from bootstrap import db


class Role(db.Model):
    """
    Represent a role.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

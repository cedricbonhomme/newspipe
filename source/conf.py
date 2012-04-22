#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010  Cédric Bonhomme - http://cedricbonhomme.org/
#
# For more information : http://bitbucket.org/cedricbonhomme/pyaggr3g470r/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2012/04/22 $"
__revision__ = "$Date: 2012/04/22 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3" 


import os
import ConfigParser
# load the configuration
config = ConfigParser.RawConfigParser()
try:
    config.read("./cfg/pyAggr3g470r.cfg")
except:
    config.read("./cfg/pyAggr3g470r.cfg-sample")
path = os.path.abspath(".")

MONGODB_ADDRESS = config.get('MongoDB', 'address')
MONGODB_PORT = int(config.get('MongoDB', 'port'))
MONGODB_USER = config.get('MongoDB', 'user')
MONGODB_PASSWORD = config.get('MongoDB', 'password')

mail_from = config.get('mail','mail_from')
mail_to = config.get('mail','mail_to')
smtp_server = config.get('mail','smtp')
username =  config.get('mail','username')
password =  config.get('mail','password')

DIASPORA_POD = config.get('misc', 'diaspora_pod')
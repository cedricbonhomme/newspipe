#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2013  Cédric Bonhomme - http://cedricbonhomme.org/
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
__date__ = "$Date: 2012/10/12 $"
__revision__ = "$Date: 2012/10/12 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

class Log(object):
    """
    Log events. Especially events relative to authentication.
    """
    def __init__(self):
        """
        Initialization of the logger.
        """
        import logging
        self.logger = logging.getLogger("pyaggr3g470r")
        hdlr = logging.FileHandler('./pyaggr3g470r/var/pyaggr3g470r.log')
        formater = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formater)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

    def info(self, message):
        """
        Log notices.
        """
        self.logger.info(message)

    def warning(self, message):
        """
        Log warnings.
        """
        self.logger.warning(message)

    def error(self, message):
        """
        Log errors.
        """
        self.logger.warning(message)

    def critical(self, message):
        """
        Log critical errors.
        """
        self.logger.critical(message)

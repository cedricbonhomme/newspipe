#! /usr/bin/env python
#-*- coding: utf-8 -*-

# JARR - A Web based news aggregator.
# Copyright (C) 2010-2016  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : https://github.com/JARR/JARR
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
__version__ = "$Revision: 0.7 $"
__date__ = "$Date: 2011/10/24 $"
__revision__ = "$Date: 2016/10/06 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "AGPLv3"

#
# This file contains the export functions of jarr.
#

from flask import jsonify

def export_json(user):
    """
    Export all articles of user in JSON.
    """
    result = []
    for feed in user.feeds:
        result.append({
                        "title": feed.title,
                        "description": feed.description,
                        "link": feed.link,
                        "site_link": feed.site_link,
                        "enabled": feed.enabled,
                        "created_date": feed.created_date.strftime('%s'),
                        "articles": [ {
                            "title": article.title,
                            "link": article.link,
                            "content": article.content,
                            "readed": article.readed,
                            "like": article.like,
                            "date": article.date.strftime('%s'),
                            "retrieved_date": article.retrieved_date.strftime('%s')
                        } for article in feed.articles ]
                    })
    return jsonify(result=result)

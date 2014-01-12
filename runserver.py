#! /usr/bin/env python
# -*- coding: utf-8 -*-

import conf
from pyaggr3g470r import app

app.run(host=conf.WEBSERVER_HOST, port=conf.WEBSERVER_PORT, \
        debug=conf.WEBSERVER_DEBUG)

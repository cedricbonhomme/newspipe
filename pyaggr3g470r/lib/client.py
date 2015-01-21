#!/usr/bin/env python
import json
import requests
import conf


def get_client(email, password):
    client = requests.session()
    client.get(conf.PLATFORM_URL + 'api/csrf', verify=False,
               data=json.dumps({'email': email,
                                'password': password}))
    return client


def get_articles(client):
    return client.get(conf.PLATFORM_URL + 'api/v1.0/articles/').json

#!/usr/bin/env python
import json
import requests
URL = 'domain.net'


def get_client(email, password):
    client = requests.session()
    client.get(URL + 'api/csrf', verify=False,
               data=json.dumps({'email': email,
                                'password': password}))
    return client


def get_articles(client):
    return client.get(URL + 'api/v1.0/articles/').json

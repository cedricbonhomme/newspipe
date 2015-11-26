Web service
===========

Articles
--------

.. code-block:: python

    >>> import requests, json
    >>> r = requests.get("https://jarr.herokuapp.com/api/v2.0/article/1s",
    ...                  headers={'Content-type': 'application/json'},
    ...                  auth=("your-nickname", "your-password"))
    >>> r.status_code
    200  # OK
    >>> rjson = r.json()
    >>> rjson["title"]
    'Sponsors required for KDE code sprint in Randa'
    >>> rjson["date"]
    'Wed, 18 Jun 2014 14:25:18 GMT'
    >>> r = requests.get("https://jarr.herokuapp.com/api/v2.0/article/1s",
    ...                  headers={'Content-type': 'application/json'},
    ...                  auth=("your-nickname", "your-password"),
    ...                  data=json.dumps({'id__in': [1, 2]}))
    >>> r.json()
    [{'id': 1, 'title': 'article1', [...]},
     {'id': 2, 'title': 'article2', [...]}]

Add an article:

.. code-block:: python

    >>> import requests, json
    >>> headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    >>> payload = {'link': 'http://blog.cedricbonhomme.org/2014/05/24/sortie-de-pyaggr3g470r-5-3/',
    ...            'title': 'Sortie de pyAggr3g470r 5.3',
    ...            'content':'La page principale de pyAggr3g470r a été améliorée...',
    ...            'date':'2014/06/23T11:42:20 GMT',
    ...            'feed_id':'42'}
    >>> r = requests.post("https://jarr.herokuapp.com/api/v2.0/article",
    ...                   headers=headers, auth=("your-nickname", "your-password"),
    ...                   data=json.dumps(payload))
    >>> r.status_code
    201  # Created
    >>> # creating several articles at once
    >>> r = requests.post("https://jarr.herokuapp.com/api/v2.0/article",
    ...                   headers=headers, auth=("your-nickname", "your-password"),
    ...                   data=json.dumps([payload, payload]))
    >>> r.status_code
    201  # Created
    >>> r.json()
    [123456, 234567]
    >>> r = requests.get("https://jarr.herokuapp.com/api/v2.0/articles",
    ...                  auth=("your-nickname", "your-password")
    ...                  data=json.dumps({'feed_id': 42, 'limit': 1}))
    >>> r.json()[0]["title"]
    "Sortie de pyAggr3g470r 5.3"

Update an article:

.. code-block:: python

    >>> import requests, json
    >>> r = requests.put("https://jarr.herokuapp.com/api/v2.0/article/65",
    ...                  headers={'Content-Type': 'application/json'},
    ...                  auth=("your-nickname", "your-password"),
    ...                  data=json.dumps({"like":True, "readed": False}))
    >>> r.status_code
    200  # OK
    >>> r = requests.put("https://jarr.herokuapp.com/api/v2.0/articles",
    ...                  headers={'Content-Type': 'application/json'},
    ...                  auth=("your-nickname", "your-password"),
    ...                  data=json.dumps([[1, {"like": True, "readed": False}],
    ...                                   [2, {"like": True, "readed": True}]]))
    >>> r.json()
    ['ok', 'ok']

Delete one or several article(s):

.. code-block:: python

    >>> import json, requests
    >>> r = requests.delete("https://jarr.herokuapp.com/api/v2.0/article/84574",
    ...                     headers={'Content-Type': 'application/json'},
    ...                     auth=("your-nickname", "your-password"))
    >>> r.status_code
    204  # deleted - No content
    >>> r = requests.delete("https://jarr.herokuapp.com/api/v2.0/article/84574",
    ...                     headers={'Content-Type': 'application/json'},
    ...                     auth=("your-nickname", "your-password"))
    >>> r.status_code
    404  # not found
    >>> r = requests.delete("https://jarr.herokuapp.com/api/v2.0/articles",
    ...                     headers={'Content-Type': 'application/json'},
    ...                     auth=("your-nickname", "your-password")
    ...                     data=json.dumps([84574]))
    >>> r.status_code
    500 # already deleted
    >>> r = requests.delete("https://jarr.herokuapp.com/api/v2.0/articles",
    ...                     headers={'Content-Type': 'application/json'},
    ...                     auth=("your-nickname", "your-password")
    ...                     data=json.dumps([84575, 84576]))
    >>> r.status_code
    204  # deleted - No content
    >>> r = requests.delete("https://jarr.herokuapp.com/api/v2.0/articles",
    ...                     headers={'Content-Type': 'application/json'},
    ...                     auth=("your-nickname", "your-password")
    ...                     data=json.dumps([84575, 84576, 84577]))
    >>> r.status_code
    206  # partial - some deleted
    >>> r.json()
    ['404 - Not Found', '404 - Not Found', 'ok']


Feeds
-----

Add a feed:

.. code-block:: python

    >>> import json, requests
    >>> r = requests.post("https://jarr.herokuapp.com/api/v2.0/feeds",
    ...                   auth=("your-nickname", "your-password"),
    ...                   headers={'Content-Type': 'application/json'},
    ...                   data=json.dumps({'link': 'http://blog.cedricbonhomme.org/feed'}))
    >>> r.status_code
    200

Update a feed:

.. code-block:: python

    >>> import json, requests
    >>> r = requests.put("https://jarr.herokuapp.com/api/v2.0/feeds/42",
    ...                  auth=("your-nickname", "your-password"),
    ...                  headers={'Content-Type': 'application/json'},
    ...                  data=json.dumps({"title":"Feed new title", "description":"New description"})
    >>> r.status_code
    201

Delete a feed:

.. code-block:: python

    >>> import requests
    >>> r = requests.delete("https://jarr.herokuapp.com/api/v2.0/feeds/29",
    ...                     auth=("your-nickname", "your-password"))

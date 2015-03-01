Web service
===========

Articles
--------

.. code-block:: python

    >>> import requests, json
    >>> r = requests.get("https://pyaggr3g470r.herokuapp.com/api/v2.0/articles",
    ...                  auth=("your-nickname", "your-password"))
    >>> r.status_code
    200  # OK
    >>> rjson = r.json()
    >>> rjson["result"][0]["title"]
    u'Sponsors required for KDE code sprint in Randa'
    >>> rjson["result"][0]["date"]
    u'Wed, 18 Jun 2014 14:25:18 GMT'

Possible parameters:

.. code-block:: bash

    $ curl --user your-nickname:your-password "https://pyaggr3g470r.herokuapp.com/api/v2.0/articles" -H 'Content-Type: application/json' --data='{"feed": 24}'

Get an article with another way to pass credentials :

.. code-block:: bash

    $ curl "https://your-nickname:your-password@pyaggr3g470r.herokuapp.com/api/v2.0/article/84566"

And delete it :

.. code-block:: bash

    $ curl -XDELETE "https://your-nickname:your-password@pyaggr3g470r.herokuapp.com/api/v2.0/article/84566"

Add an article:

.. code-block:: python

    >>> import requests, json
    >>> headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    >>> payload = {'link': 'http://blog.cedricbonhomme.org/2014/05/24/sortie-de-pyaggr3g470r-5-3/',
    ...            'title': 'Sortie de pyAggr3g470r 5.3',
    ...            'content':'La page principale de pyAggr3g470r a été améliorée...',
    ...            'date':'2014/06/23T11:42:20 GMT',
    ...            'feed_id':'42'}
    >>> r = requests.post("https://pyaggr3g470r.herokuapp.com/api/v2.0/article",
    ...                   headers=headers, auth=("your-nickname", "your-password"), data=json.dumps(payload))
    >>> print r.status_code
    201  # Created
    >>> r = requests.get("https://pyaggr3g470r.herokuapp.com/api/v2.0/articles",
    ...                  auth=("your-nickname", "your-password")
    ...                  data=json.dumps({'feed_id': 42, 'limit': 1}))
    >>> print json.loads(r.content)["result"][0]["title"]
    Sortie de pyAggr3g470r 5.3

Update an article:

.. code-block:: python

    >>> payload = {"like":True, "readed":False}
    >>> r = requests.put("https://pyaggr3g470r.herokuapp.com/api/v2.0/article/65", headers=headers, auth=("your-nickname", "your-password"), data=json.dumps(payload))
    >>> print r.status_code
    200  # OK

Delete an article:

.. code-block:: python

    >>> r = requests.delete("https://pyaggr3g470r.herokuapp.com/api/v2.0/article/84574", auth=("your-nickname", "your-password"))
    >>> print r.status_code
    204  # deleted - No content
    >>> r = requests.delete("https://pyaggr3g470r.herokuapp.com/api/v2.0/article/84574", auth=("your-nickname", "your-password"))
    >>> print r.status_code
    404  # not found

Feeds
-----

Add a feed:

.. code-block:: python

    >>> payload = {'link': 'http://blog.cedricbonhomme.org/feed'}
    >>> r = requests.post("https://pyaggr3g470r.herokuapp.com/api/v2.0/feeds", headers=headers, auth=("your-nickname", "your-password"), data=json.dumps(payload))

Update a feed:

.. code-block:: python

    >>> payload = {"title":"Feed new title", "description":"New description"}
    >>> r = requests.put("https://pyaggr3g470r.herokuapp.com/api/v2.0/feeds/42", headers=headers, auth=("your-nickname", "your-password"), data=json.dumps(payload))

Delete a feed:

.. code-block:: python

    >>> r = requests.delete("https://pyaggr3g470r.herokuapp.com/api/v2.0/feeds/29", auth=("your-nickname", "your-password"))

Web service
===========

Articles
--------

.. code:: python

    >>> import requests, json
    >>> r = requests.get("https://pyaggr3g470r.herokuapp.com/api/v1.0/articles", auth=("your-email", "your-password"))
    >>> r.status_code
    200
    >>> rjson = json.loads(r.text)
    >>> rjson["result"][0]["title"]
    u'Sponsors required for KDE code sprint in Randa'
    >>> rjson["result"][0]["date"]
    u'Wed, 18 Jun 2014 14:25:18 GMT'

Possible parameters:

.. code:: bash

    $ curl --user your-email:your-password "https://pyaggr3g470r.herokuapp.com/api/v1.0/articles?filter_=unread&feed=24"
    $ curl --user your-email:your-password "https://pyaggr3g470r.herokuapp.com/api/v1.0/articles?filter_=read&feed=24&limit=20"
    $ curl --user your-email:your-password "https://pyaggr3g470r.herokuapp.com/api/v1.0/articles?filter_=all&feed=24&limit=20"

Get an article:

.. code:: bash

    $ curl --user your-email:your-password "https://pyaggr3g470r.herokuapp.com/api/v1.0/articles/84566"

Add an article:

.. code:: python

    >>> import requests, json
    >>> headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    >>> payload = {'link': 'http://blog.cedricbonhomme.org/2014/05/24/sortie-de-pyaggr3g470r-5-3/', 'title': 'Sortie de pyAggr3g470r 5.3', 'content':'La page principale de pyAggr3g470r a été améliorée...', 'date':'06/23/2014 11:42 AM', 'feed_id':'42'}
    >>> r = requests.post("https://pyaggr3g470r.herokuapp.com/api/v1.0/articles", headers=headers, auth=("your-email", "your-password"), data=json.dumps(payload))
    >>> print r.content
    {
        "message": "ok"
    }
    >>> r = requests.get("https://pyaggr3g470r.herokuapp.com/api/v1.0/articles?feed=42&limit=1", auth=("your-email", "your-password"))
    >>> print json.loads(r.content)["result"][0]["title"]
    Sortie de pyAggr3g470r 5.3

Update an article:

.. code:: python

    >>> payload = {"like":True, "readed":False}
    >>> r = requests.put("https://pyaggr3g470r.herokuapp.com/api/v1.0/articles/65", headers=headers, auth=("your-email", "your-password"), data=json.dumps(payload))
    >>> print r.content
    {
        "message": "ok"
    }

Delete an article:

.. code:: python

    >>> r = requests.delete("https://pyaggr3g470r.herokuapp.com/api/v1.0/articles/84574", auth=("your-email", "your-password"))
    >>> print r.status_code
    200
    >>> print r.content
    {
        "message": "ok"
    }
    >>> r = requests.delete("https://pyaggr3g470r.herokuapp.com/api/v1.0/articles/84574", auth=("your-email", "your-password"))
    >>> print r.status_code
    200
    >>> print r.content
    {
        "message": "Article not found."
    }

Feeds
-----

Add a feed:

.. code:: python

    >>> payload = {'link': 'http://blog.cedricbonhomme.org/feed'}
    >>> r = requests.post("https://pyaggr3g470r.herokuapp.com/api/v1.0/feeds", headers=headers, auth=("your-email", "your-password"), data=json.dumps(payload))

Update a feed:

.. code:: python

    >>> payload = {"title":"Feed new title", "description":"New description"}
    >>> r = requests.put("https://pyaggr3g470r.herokuapp.com/api/v1.0/feeds/42", headers=headers, auth=("your-email", "your-password"), data=json.dumps(payload))

Delete a feed:

.. code:: python

    >>> r = requests.delete("https://pyaggr3g470r.herokuapp.com/api/v1.0/feeds/29", auth=("your-email", "your-password"))

"""
Here's a sum up on how it works :

CrawlerScheduler.run
    will retreive a list of feeds to be refreshed and pass result to
CrawlerScheduler.callback
    which will retreive each feed and treat result with
FeedCrawler.callback
    which will interprete the result (status_code, etag) collect ids
    and match them agaisnt pyagg which will cause
PyAggUpdater.callback
    to create the missing entries
"""

import time
import conf
import json
import logging
import requests
import feedparser
import dateutil.parser
from functools import wraps
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession
from pyaggr3g470r.lib.utils import default_handler

logger = logging.getLogger(__name__)
logging.captureWarnings(True)
API_ROOT = "api/v2.0/"


def extract_id(entry, keys=[('link', 'link'),
                            ('published', 'retrieved_date'),
                            ('updated', 'retrieved_date')], force_id=False):
    """For a given entry will return a dict that allows to identify it. The
    dict will be constructed on the uid of the entry. if that identifier is
    absent, the dict will be constructed upon the values of "keys".
    """
    entry_id = entry.get('entry_id') or entry.get('id')
    if entry_id:
        return {'entry_id': entry_id}
    if not entry_id and force_id:
        entry_id = hash("".join(entry[entry_key] for _, entry_key in keys
                                if entry_key in entry))
    else:
        ids = {}
        for entry_key, pyagg_key in keys:
            if entry_key in entry and pyagg_key not in ids:
                ids[pyagg_key] = entry[entry_key]
                if 'date' in pyagg_key:
                    ids[pyagg_key] = dateutil.parser.parse(ids[pyagg_key])\
                                                    .isoformat()
        return ids


class AbstractCrawler:
    __session__ = None
    __counter__ = 0

    def __init__(self, auth):
        self.auth = auth
        self.session = self.get_session()
        self.url = conf.PLATFORM_URL

    @classmethod
    def get_session(cls):
        """methods that allows us to treat session as a singleton"""
        if cls.__session__ is None:
            cls.__session__ = FuturesSession(
                    executor=ThreadPoolExecutor(max_workers=conf.NB_WORKER))
            cls.__session__.verify = False
        return cls.__session__

    @classmethod
    def count_on_me(cls, func):
        """A basic decorator which will count +1 at the begining of a call
        and -1 at the end. It kinda allows us to wait for the __counter__ value
        to be 0, meaning nothing is done anymore."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            cls.__counter__ += 1
            result = func(*args, **kwargs)
            cls.__counter__ -= 1
            return result
        return wrapper

    def query_pyagg(self, method, urn, data=None):
        """A wrapper for internal call, method should be ones you can find
        on requests (header, post, get, options, ...), urn the distant
        resources you want to access on pyagg, and data, the data you wanna
        transmit."""
        if data is None:
            data = {}
        method = getattr(self.session, method)
        return method("%s%s%s" % (self.url, API_ROOT, urn),
                      auth=self.auth, data=json.dumps(data,
                                                      default=default_handler),
                      headers={'Content-Type': 'application/json'})

    @classmethod
    def wait(cls):
        "See count_on_me, that method will just wait for the counter to be 0"
        time.sleep(1)
        while cls.__counter__:
            time.sleep(1)


class PyAggUpdater(AbstractCrawler):

    def __init__(self, feed, entries, headers, auth):
        self.feed = feed
        self.entries = entries
        self.headers = headers
        super(PyAggUpdater, self).__init__(auth)

    def to_article(self, entry):
        "Safe method to transorm a feedparser entry into an article"
        date = datetime.now()

        for date_key in ('published', 'updated'):
            if entry.get(date_key):
                try:
                    date = dateutil.parser.parse(entry[date_key])
                except Exception:
                    pass
                else:
                    break
        content = ''
        if entry.get('content'):
            content = entry['content'][0]['value']
        elif entry.get('summary'):
            content = entry['summary']

        return {'feed_id': self.feed['id'],
                'entry_id': extract_id(entry).get('entry_id', None),
                'link': entry.get('link', self.feed['site_link']),
                'title': entry.get('title', 'No title'),
                'readed': False, 'like': False,
                'content': content,
                'retrieved_date': date.isoformat(),
                'date': date.isoformat()}

    @AbstractCrawler.count_on_me
    def callback(self, response):
        """Will process the result from the challenge, creating missing article
        and updating the feed"""
        results = response.result().json()
        logger.debug('%r %r - %d entries were not matched and will be created',
                     self.feed['id'], self.feed['title'], len(results))
        for id_to_create in results:
            entry = self.to_article(
                    self.entries[tuple(sorted(id_to_create.items()))])
            logger.info('creating %r - %r', entry['title'], id_to_create)
            self.query_pyagg('post', 'article', entry)

        now = datetime.now()
        logger.debug('%r %r - updating feed etag %r last_mod %r',
                     self.feed['id'], self.feed['title'],
                     self.headers.get('etag'), now)

        self.query_pyagg('put', 'feed/%d' % self.feed['id'], {'error_count': 0,
                     'etag': self.headers.get('etag', ''),
                     'last_error': '',
                     'last_modified': self.headers.get('last-modified', '')})


class FeedCrawler(AbstractCrawler):

    def __init__(self, feed, auth):
        self.feed = feed
        super(FeedCrawler, self).__init__(auth)

    def clean_feed(self):
        """Will reset the errors counters on a feed that have known errors"""
        if self.feed.get('error_count') or self.feed.get('last_error'):
            self.query_pyagg('put', 'feed/%d' % self.feed['id'],
                             {'error_count': 0, 'last_error': ''})

    @AbstractCrawler.count_on_me
    def callback(self, response):
        """will fetch the feed and interprete results (304, etag) or will
        challenge pyagg to compare gotten entries with existing ones"""
        try:
            response = response.result()
            response.raise_for_status()
        except Exception as error:
            error_count = self.feed['error_count'] + 1
            logger.warn('%r %r - an error occured while fetching feed; bumping'
                        ' error count to %r', self.feed['id'],
                        self.feed['title'], error_count)
            self.query_pyagg('put', 'feed/%d' % self.feed['id'],
                             {'error_count': error_count,
                              'last_error': str(error)})
            return

        if response.status_code == 304:
            logger.info("%r %r - feed responded with 304",
                         self.feed['id'], self.feed['title'])
            self.clean_feed()
            return
        if self.feed['etag'] and response.headers.get('etag') \
                and response.headers.get('etag') == self.feed['etag']:
            logger.info("%r %r - feed responded with same etag (%d)",
                         self.feed['id'], self.feed['title'],
                         response.status_code)
            self.clean_feed()
            return
        ids, entries = [], {}
        parsed_response = feedparser.parse(response.text)
        for entry in parsed_response['entries']:
            entries[tuple(sorted(extract_id(entry).items()))] = entry
            ids.append(extract_id(entry))
        logger.debug('%r %r - found %d entries %r',
                     self.feed['id'], self.feed['title'], len(ids), ids)
        future = self.query_pyagg('get', 'articles/challenge', {'ids': ids})
        updater = PyAggUpdater(self.feed, entries, response.headers, self.auth)
        future.add_done_callback(updater.callback)


class CrawlerScheduler(AbstractCrawler):

    def __init__(self, username, password):
        self.auth = (username, password)
        super(CrawlerScheduler, self).__init__(self.auth)

    def prepare_headers(self, feed):
        """For a known feed, will construct some header dictionnary"""
        headers = {}
        if feed.get('etag', None):
            headers['If-None-Match'] = feed['etag']
        if feed.get('last_modified'):
            headers['If-Modified-Since'] = feed['last_modified']
        logger.debug('%r %r - calculated headers %r',
                     feed['id'], feed['title'], headers)
        return headers

    @AbstractCrawler.count_on_me
    def callback(self, response):
        """processes feeds that need to be fetched"""
        response = response.result()
        response.raise_for_status()
        feeds = response.json()
        logger.debug('%d to fetch %r', len(feeds), feeds)
        for feed in feeds:
            logger.info('%r %r - fetching resources',
                        feed['id'], feed['title'])
            future = self.session.get(feed['link'],
                                      headers=self.prepare_headers(feed))
            future.add_done_callback(FeedCrawler(feed, self.auth).callback)

    @AbstractCrawler.count_on_me
    def run(self, **kwargs):
        """entry point, will retreive feeds to be fetch
        and launch the whole thing"""
        logger.debug('retreving fetchable feed')
        future = self.query_pyagg('get', 'feeds/fetchable', kwargs)
        future.add_done_callback(self.callback)

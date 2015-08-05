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
import feedparser
from datetime import datetime, timedelta
from functools import wraps
from time import strftime, gmtime
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession
from pyaggr3g470r.lib.utils import default_handler, to_hash
from pyaggr3g470r.lib.feed_utils import construct_feed_from
from pyaggr3g470r.lib.article_utils import extract_id, construct_article

logger = logging.getLogger(__name__)
logging.captureWarnings(True)
API_ROOT = "api/v2.0/"


class AbstractCrawler:
    __session__ = None

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
                      headers={'Content-Type': 'application/json',
                               'User-Agent': 'pyaggr3g470r'})

    @classmethod
    def wait(cls, max_wait=300, checks=5, wait_for=2):
        "See count_on_me, that method will just wait for the counter to be 0"
        checked, second_waited = 0, 0
        checked = 0
        while True:
            time.sleep(wait_for)
            second_waited += wait_for
            if second_waited > max_wait:
                logger.warn('Exiting after %d seconds, counter at %d',
                            max_wait, len(cls.__counter__))
                break
            if cls.get_session().executor._work_queue.queue:
                checked = 0
                continue 
            checked += 1
            if checked == checks:
                break 


class PyAggUpdater(AbstractCrawler):

    def __init__(self, feed, entries, headers, parsed_feed, auth):
        self.feed = feed
        self.entries = entries
        self.headers = headers
        self.parsed_feed = parsed_feed
        super().__init__(auth)

    def callback(self, response):
        """Will process the result from the challenge, creating missing article
        and updating the feed"""
        article_created = False
        if response.result().status_code != 204:
            results = response.result().json()
            logger.debug('%r %r - %d entries were not matched '
                         'and will be created',
                         self.feed['id'], self.feed['title'], len(results))
            for id_to_create in results:
                article_created = True
                entry = construct_article(
                        self.entries[tuple(sorted(id_to_create.items()))],
                        self.feed)
                logger.info('%r %r - creating %r for %r - %r', self.feed['id'],
                            self.feed['title'], entry['title'],
                            entry['user_id'], id_to_create)
                self.query_pyagg('post', 'article', entry)

        logger.debug('%r %r - updating feed etag %r last_mod %r',
                     self.feed['id'], self.feed['title'],
                     self.headers.get('etag', ''),
                     self.headers.get('last-modified', ''))

        up_feed = {'error_count': 0, 'last_error': None,
                   'etag': self.headers.get('etag', ''),
                   'last_modified': self.headers.get('last-modified',
                                    strftime('%a, %d %b %Y %X %Z', gmtime()))}
        fresh_feed = construct_feed_from(url=self.feed['link'],
                                         fp_parsed=self.parsed_feed)
        for key in ('description', 'site_link', 'icon_url'):
            if fresh_feed.get(key) and fresh_feed[key] != self.feed.get(key):
                up_feed[key] = fresh_feed[key]
        if not self.feed.get('title'):
            up_feed['title'] = fresh_feed.get('title', '')
        up_feed['user_id'] = self.feed['user_id']
        # re-getting that feed earlier since new entries appeared
        if article_created:
            up_feed['last_retrieved'] \
                    = (datetime.now() - timedelta(minutes=45)).isoformat()

        if any([up_feed[key] != self.feed.get(key) for key in up_feed]):
            logger.warn('%r %r - pushing feed attrs %r',
                    self.feed['id'], self.feed['title'],
                    {key: "%s -> %s" % (up_feed[key], self.feed.get(key))
                     for key in up_feed if up_feed[key] != self.feed.get(key)})

            future = self.query_pyagg('put',
                    'feed/%d' % self.feed['id'], up_feed)


class FeedCrawler(AbstractCrawler):

    def __init__(self, feed, auth):
        self.feed = feed
        super().__init__(auth)

    def clean_feed(self):
        """Will reset the errors counters on a feed that have known errors"""
        if self.feed.get('error_count') or self.feed.get('last_error'):
            future = self.query_pyagg('put', 'feed/%d' % self.feed['id'],
                                      {'error_count': 0, 'last_error': ''})

    def callback(self, response):
        """will fetch the feed and interprete results (304, etag) or will
        challenge pyagg to compare gotten entries with existing ones"""
        try:
            response = response.result()
            response.raise_for_status()
        except Exception as error:
            error_count = self.feed['error_count'] + 1
            logger.error('%r %r - an error occured while fetching '
                         'feed; bumping  error count to %r', self.feed['id'],
                         self.feed['title'], error_count)
            future = self.query_pyagg('put', 'feed/%d' % self.feed['id'],
                                      {'error_count': error_count,
                                       'last_error': str(error),
                                       'user_id': self.feed['user_id']})
            return

        if response.status_code == 304:
            logger.info("%r %r - feed responded with 304",
                        self.feed['id'], self.feed['title'])
            self.clean_feed()
            return
        if 'etag' not in response.headers:
            logger.debug('%r %r - manually generating etag',
                         self.feed['id'], self.feed['title'])
            response.headers['etag'] = 'pyagg/"%s"' % to_hash(response.text)
        if response.headers['etag'] and self.feed['etag'] \
                and response.headers['etag'] == self.feed['etag']:
            if 'pyagg' in self.feed['etag']:
                logger.info("%r %r - calculated hash matches (%d)",
                            self.feed['id'], self.feed['title'],
                            response.status_code)
            else:
                logger.info("%r %r - feed responded with same etag (%d)",
                            self.feed['id'], self.feed['title'],
                            response.status_code)
            self.clean_feed()
            return
        else:
            logger.debug('%r %r - etag mismatch %r != %r',
                         self.feed['id'], self.feed['title'],
                         response.headers['etag'], self.feed['etag'])
        logger.info('%r %r - cache validation failed, challenging entries',
                    self.feed['id'], self.feed['title'])

        ids, entries = [], {}
        parsed_response = feedparser.parse(response.content)
        for entry in parsed_response['entries']:
            entry_ids = extract_id(entry)
            entry_ids['feed_id'] = self.feed['id']
            entry_ids['user_id'] = self.feed['user_id']
            entries[tuple(sorted(entry_ids.items()))] = entry
            ids.append(entry_ids)
        logger.debug('%r %r - found %d entries %r',
                     self.feed['id'], self.feed['title'], len(ids), ids)
        future = self.query_pyagg('get', 'articles/challenge', {'ids': ids})
        updater = PyAggUpdater(self.feed, entries, response.headers,
                               parsed_response, self.auth)
        future.add_done_callback(updater.callback)


class CrawlerScheduler(AbstractCrawler):

    def __init__(self, username, password):
        self.auth = (username, password)
        super(CrawlerScheduler, self).__init__(self.auth)

    def prepare_headers(self, feed):
        """For a known feed, will construct some header dictionnary"""
        headers = {'User-Agent': 'pyaggr3g470r/crawler'}
        if feed.get('last_modified'):
            headers['If-Modified-Since'] = feed['last_modified']
        if feed.get('etag') and 'pyagg' not in feed['etag']:
            headers['If-None-Match'] = feed['etag']
        logger.debug('%r %r - calculated headers %r',
                     feed['id'], feed['title'], headers)
        return headers

    def callback(self, response):
        """processes feeds that need to be fetched"""
        response = response.result()
        response.raise_for_status()
        if response.status_code == 204:
            logger.debug("No feed to fetch")
            return
        feeds = response.json()
        logger.debug('%d to fetch %r', len(feeds), feeds)
        for feed in feeds:
            logger.debug('%r %r - fetching resources',
                         feed['id'], feed['title'])
            future = self.session.get(feed['link'],
                                      headers=self.prepare_headers(feed))
            future.add_done_callback(FeedCrawler(feed, self.auth).callback)

    def run(self, **kwargs):
        """entry point, will retreive feeds to be fetch
        and launch the whole thing"""
        logger.debug('retreving fetchable feed')
        future = self.query_pyagg('get', 'feeds/fetchable', kwargs)
        future.add_done_callback(self.callback)

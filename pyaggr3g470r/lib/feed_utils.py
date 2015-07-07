import urllib
import logging
import requests
import feedparser
from bs4 import BeautifulSoup, SoupStrainer

from pyaggr3g470r.lib.utils import try_keys, try_splits, rebuild_url

logger = logging.getLogger(__name__)


def construct_feed_from(url=None, fp_parsed=None, feed=None, query_site=True):
    if url is None and fp_parsed is not None:
        url = fp_parsed.get('url')
    if url is not None and fp_parsed is None:
        try:
            response = requests.get(url, verify=False)
            fp_parsed = feedparser.parse(response.content,
                                         request_headers=response.headers)
        except Exception:
            logger.exception('failed to retreive that url')
            fp_parsed = {'bozo': True}
    assert url is not None and fp_parsed is not None
    feed = feed or {}
    feed_split = urllib.parse.urlsplit(url)
    site_split = None
    if not fp_parsed['bozo']:
        feed['link'] = url
        feed['site_link'] = try_keys(fp_parsed['feed'], 'href', 'link')
        feed['title'] = fp_parsed['feed'].get('title')
        feed['description'] = try_keys(fp_parsed['feed'], 'subtitle', 'title')
        feed['icon'] = try_keys(fp_parsed['feed'], 'icon')
    else:
        feed['site_link'] = url

    if feed.get('site_link'):
        feed['site_link'] = rebuild_url(feed['site_link'], feed_split)
        site_split = urllib.parse.urlsplit(feed['site_link'])

    if feed.get('icon'):
        feed['icon'] = try_splits(feed['icon'], site_split, feed_split)
        if feed['icon'] is None:
            del feed['icon']

    if not feed.get('site_link') or not query_site \
            or all(bool(feed.get(key)) for key in ('link', 'title', 'icon')):
        return feed

    response = requests.get(feed['site_link'], verify=False)
    bs_parsed = BeautifulSoup(response.content, 'html.parser',
                              parse_only=SoupStrainer('head'))

    if not feed.get('title'):
        try:
            feed['title'] = bs_parsed.find_all('title')[0].text
        except Exception:
            pass

    def check_keys(**kwargs):
        def wrapper(elem):
            for key, vals in kwargs.items():
                if not elem.has_attr(key):
                    return False
                if not all(val in elem.attrs[key] for val in vals):
                    return False
            return True
        return wrapper

    if not feed.get('icon'):
        icons = bs_parsed.find_all(check_keys(rel=['icon', 'shortcut']))
        if not len(icons):
            icons = bs_parsed.find_all(check_keys(rel=['icon']))
        if len(icons) >= 1:
            for icon in icons:
                feed['icon'] = try_splits(icon.attrs['href'],
                                          site_split, feed_split)
                if feed['icon'] is not None:
                    break

        if feed.get('icon') is None:
            feed['icon'] = try_splits('/favicon.ico', site_split, feed_split)
        if 'icon' in feed and feed['icon'] is None:
            del feed['icon']

    if not feed.get('link'):
        alternates = bs_parsed.find_all(check_keys(rel=['alternate'],
                type=['application/rss+xml']))
        if len(alternates) >= 1:
            feed['link'] = rebuild_url(alternates[0].attrs['href'], feed_split)
    return feed

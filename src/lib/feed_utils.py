import html
import urllib
import logging
import requests
import feedparser
from conf import CRAWLER_USER_AGENT
from bs4 import BeautifulSoup, SoupStrainer

from lib.utils import try_keys, try_get_icon_url, rebuild_url

logger = logging.getLogger(__name__)
logging.captureWarnings(True)
ACCEPTED_MIMETYPES = ('application/rss+xml', 'application/rdf+xml',
                      'application/atom+xml', 'application/xml', 'text/xml')


def is_parsing_ok(parsed_feed):
    return parsed_feed['entries'] or not parsed_feed['bozo']


def escape_keys(*keys):
    def wrapper(func):
        def metawrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            for key in keys:
                if key in result:
                    result[key] = html.unescape(result[key] or '')
            return result
        return metawrapper
    return wrapper


@escape_keys('title', 'description')
def construct_feed_from(url=None, fp_parsed=None, feed=None, query_site=True):
    requests_kwargs = {'headers': {'User-Agent': CRAWLER_USER_AGENT},
                        'verify': False}
    if url is None and fp_parsed is not None:
        url = fp_parsed.get('url')
    if url is not None and fp_parsed is None:
        try:
            response = requests.get(url, **requests_kwargs)
            fp_parsed = feedparser.parse(response.content,
                                         request_headers=response.headers)
        except Exception:
            logger.exception('failed to retrieve that url')
            fp_parsed = {'bozo': True}
    assert url is not None and fp_parsed is not None
    feed = feed or {}
    feed_split = urllib.parse.urlsplit(url)
    site_split = None
    if is_parsing_ok(fp_parsed):
        feed['link'] = url
        feed['site_link'] = try_keys(fp_parsed['feed'], 'href', 'link')
        feed['title'] = fp_parsed['feed'].get('title')
        feed['description'] = try_keys(fp_parsed['feed'], 'subtitle', 'title')
        feed['icon_url'] = try_keys(fp_parsed['feed'], 'icon')
    else:
        feed['site_link'] = url

    if feed.get('site_link'):
        feed['site_link'] = rebuild_url(feed['site_link'], feed_split)
        site_split = urllib.parse.urlsplit(feed['site_link'])

    if feed.get('icon_url'):
        feed['icon_url'] = try_get_icon_url(
                feed['icon_url'], site_split, feed_split)
        if feed['icon_url'] is None:
            del feed['icon_url']

    if not feed.get('site_link') or not query_site \
            or all(bool(feed.get(k)) for k in ('link', 'title', 'icon_url')):
        return feed

    try:
        response = requests.get(feed['site_link'], **requests_kwargs)
    except Exception:
        logger.exception('failed to retrieve %r', feed['site_link'])
        return feed
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

    if not feed.get('icon_url'):
        icons = bs_parsed.find_all(check_keys(rel=['icon', 'shortcut']))
        if not len(icons):
            icons = bs_parsed.find_all(check_keys(rel=['icon']))
        if len(icons) >= 1:
            for icon in icons:
                feed['icon_url'] = try_get_icon_url(icon.attrs['href'],
                                                    site_split, feed_split)
                if feed['icon_url'] is not None:
                    break

        if feed.get('icon_url') is None:
            feed['icon_url'] = try_get_icon_url('/favicon.ico',
                                                site_split, feed_split)
        if 'icon_url' in feed and feed['icon_url'] is None:
            del feed['icon_url']

    if not feed.get('link'):
        for type_ in ACCEPTED_MIMETYPES:
            alternates = bs_parsed.find_all(check_keys(
                    rel=['alternate'], type=[type_]))
            if len(alternates) >= 1:
                feed['link'] = rebuild_url(alternates[0].attrs['href'],
                                           feed_split)
                break
    return feed

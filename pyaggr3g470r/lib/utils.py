import types
import urllib
import requests
import feedparser
from bs4 import BeautifulSoup, SoupStrainer


def default_handler(obj):
    """JSON handler for default query formatting"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    if hasattr(obj, 'dump'):
        return obj.dump()
    if isinstance(obj, (set, frozenset, types.GeneratorType)):
        return list(obj)
    if isinstance(obj, BaseException):
        return str(obj)
    raise TypeError("Object of type %s with value of %r "
                    "is not JSON serializable" % (type(obj), obj))


def try_keys(dico, *keys):
    for key in keys:
        if key in dico:
            return dico[key]
    return


def rebuild_url(url, base_split):
    split = urllib.parse.urlsplit(url)
    if split.scheme and split.netloc:
        return url  # url is fine
    new_split = urllib.parse.SplitResult(
            scheme=split.scheme or base_split.scheme,
            netloc=split.netloc or base_split.netloc,
            path=split.path, query='', fragment='')
    return urllib.parse.urlunsplit(new_split)


def try_splits(url, *splits):
    for split in splits:
        if requests.get(rebuild_url(url, split), verify=False).ok:
            return rebuild_url(url, split)
    return None


def construct_feed_from(url=None, fp_parsed=None, feed=None, query_site=True):
    if url is None and fp_parsed is not None:
        url = fp_parsed.get('url')
    if url is not None and fp_parsed is None:
        response = requests.get(url, verify=False)
        fp_parsed = feedparser.parse(response.content)
    assert url is not None and fp_parsed is not None
    feed = feed or {}
    feed_split = urllib.parse.urlsplit(url)
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

        if feed['icon'] is None:
            feed['icon'] = try_splits('/favicon.ico', site_split, feed_split)
        if feed['icon'] is None:
            del feed['icon']

    if not feed.get('link'):
        alternate = bs_parsed.find_all(check_keys(rel=['alternate'],
                type=['application/rss+xml']))
        if len(alternate) == 1:
            feed['link'] = rebuild_url(alternate[0].attrs['href'], split)
        elif len(alternate) > 1:
            feed['link'] = rebuild_url(alternate[0].attrs['href'], split)
            feed['other_link'] = [rebuild_url(al.attrs['href'], split)
                                  for al in alternate[1:]]
    return feed

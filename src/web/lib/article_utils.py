import logging
import requests
import dateutil.parser
from datetime import datetime

import conf
from web.lib.utils import to_hash

logger = logging.getLogger(__name__)


def extract_id(entry, keys=[('link', 'link'), ('published', 'date'),
                            ('updated', 'date')], force_id=False):
    """For a given entry will return a dict that allows to identify it. The
    dict will be constructed on the uid of the entry. if that identifier is
    absent, the dict will be constructed upon the values of "keys".
    """
    entry_id = entry.get('entry_id') or entry.get('id')
    if entry_id:
        return {'entry_id': entry_id}
    if not entry_id and force_id:
        return to_hash("".join(entry[entry_key] for _, entry_key in keys
                                   if entry_key in entry).encode('utf8'))
    else:
        ids = {}
        for entry_key, pyagg_key in keys:
            if entry_key in entry and pyagg_key not in ids:
                ids[pyagg_key] = entry[entry_key]
                if 'date' in pyagg_key:
                    ids[pyagg_key] = dateutil.parser.parse(ids[pyagg_key])\
                                                    .isoformat()
        return ids


def construct_article(entry, feed):
    if hasattr(feed, 'dump'):  # this way can be a sqlalchemy obj or a dict
        feed = feed.dump()
    "Safe method to transorm a feedparser entry into an article"
    now = datetime.now()
    date = None
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

    article_link = entry.get('link')
    if conf.RESOLVE_ARTICLE_URL and article_link:
        try:
            # resolves URL behind proxies
            # (like feedproxy.google.com)
            response = requests.get(article_link, verify=False, timeout=5.0)
            article_link = response.url
        except Exception as error:
            logger.warning("Unable to get the real URL of %s. Error: %s",
                           article_link, error)

    return {'feed_id': feed['id'],
            'user_id': feed['user_id'],
            'entry_id': extract_id(entry).get('entry_id', None),
            'link': entry.get('link', feed['site_link']),
            'title': entry.get('title', 'No title'),
            'readed': False, 'like': False,
            'content': content,
            'retrieved_date': now.isoformat(),
            'date': (date or now).isoformat()}

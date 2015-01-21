import feedparser
import dateutil.parser.parse


def get_feed_content(feed):
    etag = feed.get('etag', None)
    last_modified = None
    if feed.get('last_modified'):
        last_modified = dateutil.parser.parse(feed['last_modified'])\
                                    .strftime('%a, %d %b %Y %H:%M:%S %Z')
    return feedparser.parse(feed['link'], etag=etag, modified=last_modified)

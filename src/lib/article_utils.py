import html
import logging
import re
from datetime import datetime, timezone
from enum import Enum
from urllib.parse import SplitResult, urlsplit, urlunsplit

import dateutil.parser
from bs4 import BeautifulSoup, SoupStrainer
from requests.exceptions import MissingSchema

import conf
from lib.utils import jarr_get

logger = logging.getLogger(__name__)
PROCESSED_DATE_KEYS = {'published', 'created', 'updated'}


def extract_id(entry):
    """ extract a value from an entry that will identify it among the other of
    that feed"""
    return entry.get('entry_id') or entry.get('id') or entry['link']


async def construct_article(entry, feed, fields=None, fetch=True):
    "Safe method to transform a feedparser entry into an article"
    now = datetime.utcnow()
    article = {}
    def push_in_article(key, value):
        if not fields or key in fields:
            article[key] = value
    push_in_article('feed_id', feed.id)
    push_in_article('user_id', feed.user_id)
    push_in_article('entry_id', extract_id(entry))
    push_in_article('retrieved_date', now)
    if not fields or 'date' in fields:
        for date_key in PROCESSED_DATE_KEYS:
            if entry.get(date_key):
                try:
                    article['date'] = dateutil.parser.parse(entry[date_key])\
                            .astimezone(timezone.utc)
                except Exception as e:
                    logger.exception(e)
                else:
                    break
    push_in_article('content', get_article_content(entry))
    if fields is None or {'link', 'title'}.intersection(fields):
        link, title = await get_article_details(entry, fetch)
        push_in_article('link', link)
        push_in_article('title', title)
        if 'content' in article:
            #push_in_article('content', clean_urls(article['content'], link))
            push_in_article('content', article['content'])
    push_in_article('tags', {tag.get('term').strip()
                             for tag in entry.get('tags', []) \
                                    if tag and tag.get('term', False)})
    return article


def get_article_content(entry):
    content = ''
    if entry.get('content'):
        content = entry['content'][0]['value']
    elif entry.get('summary'):
        content = entry['summary']
    return content


async def get_article_details(entry, fetch=True):
    article_link = entry.get('link')
    article_title = html.unescape(entry.get('title', ''))
    if fetch and conf.CRAWLER_RESOLV and article_link or not article_title:
        try:
            # resolves URL behind proxies (like feedproxy.google.com)
            response = await jarr_get(article_link, timeout=5)
        except MissingSchema:
            split, failed = urlsplit(article_link), False
            for scheme in 'https', 'http':
                new_link = urlunsplit(SplitResult(scheme, *split[1:]))
                try:
                    response = await jarr_get(new_link, timeout=5)
                except Exception as error:
                    failed = True
                    continue
                failed = False
                article_link = new_link
                break
            if failed:
                return article_link, article_title or 'No title'
        except Exception as error:
            logger.info("Unable to get the real URL of %s. Won't fix "
                        "link or title. Error: %s", article_link, error)
            return article_link, article_title or 'No title'
        article_link = response.url
        if not article_title:
            bs_parsed = BeautifulSoup(response.content, 'html.parser',
                                      parse_only=SoupStrainer('head'))
            try:
                article_title = bs_parsed.find_all('title')[0].text
            except IndexError:  # no title
                pass
    return article_link, article_title or 'No title'


class FiltersAction(Enum):
    READ = 'mark as read'
    LIKED = 'mark as favorite'
    SKIP = 'skipped'


class FiltersType(Enum):
    REGEX = 'regex'
    MATCH = 'simple match'
    EXACT_MATCH = 'exact match'
    TAG_MATCH = 'tag match'
    TAG_CONTAINS = 'tag contains'


class FiltersTrigger(Enum):
    MATCH = 'match'
    NO_MATCH = 'no match'


def process_filters(filters, article, only_actions=None):
    skipped, read, liked = False, None, False
    filters = filters or []
    if only_actions is None:
        only_actions = set(FiltersAction)
    for filter_ in filters:
        match = False
        try:
            pattern = filter_.get('pattern', '')
            filter_type = FiltersType(filter_.get('type'))
            filter_action = FiltersAction(filter_.get('action'))
            filter_trigger = FiltersTrigger(filter_.get('action on'))
            if filter_type is not FiltersType.REGEX:
                pattern = pattern.lower()
        except ValueError:
            continue
        if filter_action not in only_actions:
            logger.debug('ignoring filter %r' % filter_)
            continue
        if filter_action in {FiltersType.REGEX, FiltersType.MATCH,
                FiltersType.EXACT_MATCH} and 'title' not in article:
            continue
        if filter_action in {FiltersType.TAG_MATCH, FiltersType.TAG_CONTAINS} \
                and 'tags' not in article:
            continue
        title = article.get('title', '').lower()
        tags = [tag.lower() for tag in article.get('tags', [])]
        if filter_type is FiltersType.REGEX:
            match = re.match(pattern, title)
        elif filter_type is FiltersType.MATCH:
            match = pattern in title
        elif filter_type is FiltersType.EXACT_MATCH:
            match = pattern == title
        elif filter_type is FiltersType.TAG_MATCH:
            match = pattern in tags
        elif filter_type is FiltersType.TAG_CONTAINS:
            match = any(pattern in tag for tag in tags)
        take_action = match and filter_trigger is FiltersTrigger.MATCH \
                or not match and filter_trigger is FiltersTrigger.NO_MATCH

        if not take_action:
            continue

        if filter_action is FiltersAction.READ:
            read = True
        elif filter_action is FiltersAction.LIKED:
            liked = True
        elif filter_action is FiltersAction.SKIP:
            skipped = True

    if skipped or read or liked:
        logger.info("%r applied on %r", filter_action.value,
                    article.get('link') or article.get('title'))
    return skipped, read, liked


def get_skip_and_ids(entry, feed):
    entry_ids = construct_article(entry, feed,
                {'entry_id', 'feed_id', 'user_id'}, fetch=False)
    skipped, _, _ = process_filters(feed.filters,
            construct_article(entry, feed, {'title', 'tags'}, fetch=False),
            {FiltersAction.SKIP})
    return skipped, entry_ids

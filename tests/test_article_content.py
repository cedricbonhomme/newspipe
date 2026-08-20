# The body stored for an article must be the feed's full content, not a caption.
#
# feedparser puts every content-ish element into ``entry["content"]``, including
# the ``<media:description>`` of a ``<media:content>`` image. Feeds that carry
# both (404 Media, and every other Ghost-generated feed) list that caption
# *before* ``<content:encoded>``, so reading ``content[0]`` silently stored a
# one-line caption as the whole article. These tests pin the selection down.
import feedparser

from newspipe.lib.article_utils import get_article_content

CAPTION = "A one-line image caption"
BODY = "<p>The full article body, several paragraphs long.</p>"

FEED = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:media="http://search.yahoo.com/mrss/" version="2.0">
  <channel>
    <title>Example</title>
    <item>
      <title>An article</title>
      <description><![CDATA[A short teaser.]]></description>
      <link>https://example.com/an-article/</link>
      <media:content url="https://example.com/hero.jpg" medium="image">
        <media:description type="plain">{CAPTION}</media:description>
      </media:content>
      <content:encoded><![CDATA[{BODY}]]></content:encoded>
    </item>
  </channel>
</rss>
"""


def test_media_caption_does_not_shadow_the_real_content():
    entry = feedparser.parse(FEED).entries[0]
    # Guard the premise: the caption really does come first.
    assert entry["content"][0]["value"] == CAPTION
    assert get_article_content(entry) == BODY


def test_html_content_is_preferred_over_a_longer_plain_one():
    entry = {
        "content": [
            {"type": "text/plain", "value": "x" * 500},
            {"type": "text/html", "value": BODY},
        ]
    }
    assert get_article_content(entry) == BODY


def test_longest_html_content_wins():
    entry = {
        "content": [
            {"type": "text/html", "value": "<p>short</p>"},
            {"type": "text/html", "value": BODY},
        ]
    }
    assert get_article_content(entry) == BODY


def test_summary_wins_over_a_bare_caption():
    summary = "<p>A summary that says more than the caption.</p>"
    entry = {"content": [{"type": "text/plain", "value": CAPTION}], "summary": summary}
    assert get_article_content(entry) == summary


def test_summary_is_used_when_there_is_no_content():
    entry = {"summary": BODY}
    assert get_article_content(entry) == BODY


def test_entry_without_body_yields_empty_string():
    assert get_article_content({}) == ""

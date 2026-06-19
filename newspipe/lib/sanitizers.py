import bleach  # type: ignore[import-untyped]

from newspipe.lib.constants import ALLOWED_ATTRIBUTES
from newspipe.lib.constants import ALLOWED_TAGS


def sanitize_html_fragment(raw_html: str) -> str:
    """Clean an HTML fragment of malicious content and return it.

    Disallowed tags are stripped (removed) rather than escaped, so the
    sanitizer never leaks literal ``<tag>`` text into the rendered article.
    """
    return bleach.clean(
        raw_html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )


def sanitize_text(raw_text: str) -> str:
    return bleach.clean(raw_text, tags=[], attributes={}, strip=True)

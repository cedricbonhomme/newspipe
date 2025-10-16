import bleach  # type: ignore[import-untyped]

ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS) | {
    "a",
    "abbr",
    "b",
    "i",
    "img",
    "blockquote",
    "code",
    "table",
    "thead",
    "tbody",
    "th",
    "tr",
    "td",
    "em",
    "p",
    "pre",
    "strong",
    "ul",
    "ol",
    "li",
    "br",
    "hr",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
}

ALLOWED_ATTRIBUTES: dict[str, list[str]] = {
    "a": ["href", "title"],
    "img": ["src", "alt", "title"],
}


# Free email providers
FREE_EMAIL_DOMAINS = {
    "gmail.com",
    "hotmail.com",
    "outlook.com",
    "yahoo.com",
    "live.com",
    "aol.com",
    "icloud.com",
    "msn.com",
    "protonmail.com",
    "zoho.com",
    "mail.com",
    "gmx.com",
    "yandex.com",
    "pm.me",
    "tutanota.com",
    "fastmail.com",
    "inbox.com",
    "hushmail.com",
}

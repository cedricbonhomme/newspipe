"""Build the /.well-known/security.txt file (RFC 9116) from the configuration."""


def render_security_txt(fields):
    """Return the security.txt body for the given fields.

    ``fields`` maps a field name (e.g. "Contact") to a value or a list of values
    (a field such as Contact may appear several times). Fields are written in
    the order of the mapping. Empty values are skipped.
    """
    lines = []
    for name, values in fields.items():
        if isinstance(values, str):
            values = [values]
        for value in values:
            value = str(value).strip()
            if not value:
                continue
            if "\n" in value or "\r" in value:
                raise ValueError(f"security.txt field {name!r} must be on one line")
            lines.append(f"{name}: {value}")
    return "\n".join(lines) + "\n" if lines else ""

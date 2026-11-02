import pytest

from newspipe.lib.security_txt import render_security_txt


def test_fields_in_order_and_repeated():
    body = render_security_txt(
        {
            "Contact": ["mailto:a@example.org", "https://example.org/contact"],
            "Expires": "2027-10-31T23:00:00.000Z",
        }
    )
    assert body == (
        "Contact: mailto:a@example.org\n"
        "Contact: https://example.org/contact\n"
        "Expires: 2027-10-31T23:00:00.000Z\n"
    )


def test_empty_values_skipped_and_empty_config():
    assert render_security_txt({"Contact": "", "Policy": []}) == ""
    assert render_security_txt({}) == ""


def test_newline_in_value_rejected():
    with pytest.raises(ValueError):
        render_security_txt({"Contact": "mailto:a@example.org\nPolicy: evil"})

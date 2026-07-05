#! /usr/bin/env python
# Newspipe - A web news aggregator.
# Copyright (C) 2010-2026 Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information: https://github.com/cedricbonhomme/newspipe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import json
import secrets
import time

import pyotp
import qrcode.image.svg
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from newspipe.bootstrap import application

RECOVERY_CODES_COUNT = 10


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def provisioning_uri(user) -> str:
    # The issuer is displayed in the user's authenticator application: use the
    # public address of the instance so users with accounts on several
    # Newspipe instances can tell them apart.
    issuer = application.config.get("TOTP_ISSUER", "Newspipe")
    return pyotp.totp.TOTP(user.totp_secret).provisioning_uri(
        name=user.nickname, issuer_name=issuer
    )


def qrcode_svg(user) -> str:
    """
    Return the enrollment QR code as an inline SVG string.
    """
    img = qrcode.make(
        provisioning_uri(user),
        image_factory=qrcode.image.svg.SvgPathFillImage,
        box_size=12,
    )
    return img.to_string(encoding="unicode")


def verify_totp(user, code: str):
    """
    Verify a TOTP code against the current and the previous timestep.

    Return the matched timestep so the caller can persist it (replay
    protection: a timestep lower or equal to user.last_totp is rejected),
    or None if the code is invalid.
    """
    if not user.totp_secret:
        return None
    code = code.strip().replace(" ", "")
    totp = pyotp.TOTP(user.totp_secret)
    timecode = int(time.time()) // totp.interval
    for counter in (timecode, timecode - 1):
        if user.last_totp is not None and counter <= user.last_totp:
            continue
        if pyotp.utils.strings_equal(code, totp.generate_otp(counter)):
            return counter
    return None


def generate_recovery_codes():
    """
    Return a tuple (codes, hashes_json): the plaintext recovery codes to
    display once to the user, and the JSON list of their hashes to store.
    """
    codes = [
        "-".join(secrets.token_hex(2) for _ in range(3))
        for _ in range(RECOVERY_CODES_COUNT)
    ]
    hashes = [generate_password_hash(code) for code in codes]
    return codes, json.dumps(hashes)


def consume_recovery_code(user, code: str):
    """
    Check a recovery code against the stored hashes. If it matches, return
    the updated JSON list with the used code removed (a recovery code is
    only valid once). Return None if the code is invalid.
    """
    if not user.recovery_codes:
        return None
    code = code.strip().lower().replace(" ", "")
    hashes = json.loads(user.recovery_codes)
    for candidate in hashes:
        if check_password_hash(candidate, code):
            hashes.remove(candidate)
            return json.dumps(hashes)
    return None


def remaining_recovery_codes(user) -> int:
    if not user.recovery_codes:
        return 0
    return len(json.loads(user.recovery_codes))

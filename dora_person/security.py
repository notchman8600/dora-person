"""JWT helpers for issuing and validating session tokens."""

import datetime
from typing import Any

from jwt import decode, encode

from dora_person.config import Settings


def create_access_token(claims: dict[str, Any], settings: Settings) -> str:
    """Encode ``claims`` into a signed JWT with an expiry derived from settings."""

    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=settings.token_expire_minutes)
    payload = {**claims, "exp": expire}
    return encode(payload, settings.signing_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> dict[str, Any]:
    """Decode and verify a JWT, raising the underlying ``jwt`` errors on failure."""

    return decode(token, settings.signing_key, algorithms=[settings.jwt_algorithm])

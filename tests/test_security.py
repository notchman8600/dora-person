import datetime

import pytest
from jwt import ExpiredSignatureError

from dora_person.config import Settings
from dora_person.security import create_access_token, decode_access_token


def test_round_trip_preserves_claims():
    settings = Settings(secret_key="k")
    token = create_access_token({"github_name": "octocat", "avatar_url": "https://a/x"}, settings)

    claims = decode_access_token(token, settings)

    assert claims["github_name"] == "octocat"
    assert claims["avatar_url"] == "https://a/x"
    assert "exp" in claims


def test_expired_token_is_rejected():
    settings = Settings(secret_key="k", token_expire_minutes=-1)
    token = create_access_token({"github_name": "octocat"}, settings)

    with pytest.raises(ExpiredSignatureError):
        decode_access_token(token, settings)


def test_expiry_uses_configured_window():
    settings = Settings(secret_key="k", token_expire_minutes=15)
    before = datetime.datetime.now(datetime.UTC)

    claims = decode_access_token(create_access_token({}, settings), settings)

    exp = datetime.datetime.fromtimestamp(claims["exp"], tz=datetime.UTC)
    assert datetime.timedelta(minutes=14) < (exp - before) <= datetime.timedelta(minutes=15)


def test_signing_key_required():
    with pytest.raises(RuntimeError):
        create_access_token({}, Settings(secret_key=None))

import httpx
import pytest
import respx

from dora_person.config import Settings
from dora_person.errors import GitHubOAuthError
from dora_person.services.github import GitHubGateway


def gateway() -> GitHubGateway:
    return GitHubGateway(Settings(client_id="cid", client_secret="secret", redirect_url="https://cb.test"))


def test_authorize_url_includes_client_and_redirect():
    url = gateway().authorize_url()

    assert url == "https://github.com/login/oauth/authorize?client_id=cid&redirect_uri=https://cb.test"


@respx.mock
async def test_exchange_code_returns_access_token():
    respx.post("https://github.com/login/oauth/access_token").mock(
        return_value=httpx.Response(200, json={"access_token": "gho_token"})
    )

    assert await gateway().exchange_code_for_token("abc") == "gho_token"


@respx.mock
async def test_exchange_code_raises_on_error():
    respx.post("https://github.com/login/oauth/access_token").mock(
        return_value=httpx.Response(200, json={"error": "bad_verification_code"})
    )

    with pytest.raises(GitHubOAuthError, match="bad_verification_code"):
        await gateway().exchange_code_for_token("abc")


@respx.mock
async def test_fetch_profile_encodes_avatar():
    respx.get("https://api.github.com/user").mock(
        return_value=httpx.Response(200, json={"id": 42, "login": "octocat", "avatar_url": "https://a/x?y=1"})
    )

    profile = await gateway().fetch_profile("gho_token")

    assert profile.user_id == 42
    assert profile.user_name == "octocat"
    assert profile.avatar_url == "https%3A//a/x%3Fy%3D1"

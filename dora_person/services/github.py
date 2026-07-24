"""Gateway encapsulating all outbound calls to GitHub's OAuth and REST APIs."""

import httpx

from dora_person.config import Settings
from dora_person.errors import GitHubOAuthError
from dora_person.schemas import GitHubProfile

_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
_USER_URL = "https://api.github.com/user"


class GitHubGateway:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def authorize_url(self) -> str:
        """Build the URL that starts the OAuth authorization flow."""

        return (
            "https://github.com/login/oauth/authorize"
            f"?client_id={self._settings.client_id}&redirect_uri={self._settings.redirect_url}"
        )

    async def exchange_code_for_token(self, code: str) -> str:
        """Exchange an OAuth ``code`` for an access token.

        Raises :class:`GitHubOAuthError` when GitHub reports an error.
        """

        data = {
            "client_id": self._settings.client_id,
            "client_secret": self._settings.client_secret,
            "code": code,
        }
        headers = {"Accept": "application/json"}
        async with httpx.AsyncClient() as client:
            response = await client.post(_ACCESS_TOKEN_URL, data=data, headers=headers)
        body = response.json()
        if "error" in body:
            raise GitHubOAuthError(body["error"])
        return body["access_token"]

    async def fetch_profile(self, access_token: str) -> GitHubProfile:
        """Fetch the authenticated user's profile using ``access_token``."""

        async with httpx.AsyncClient() as client:
            response = await client.get(_USER_URL, headers={"Authorization": f"token {access_token}"})
        profile = response.json()
        return GitHubProfile(
            user_id=profile["id"],
            user_name=profile["login"],
            avatar_url=profile["avatar_url"],
        )

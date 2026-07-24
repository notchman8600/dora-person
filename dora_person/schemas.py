"""Data transfer objects passed between the router, service and view layers."""

from dataclasses import dataclass
from urllib.parse import quote, unquote


@dataclass
class GitHubProfile:
    """A GitHub user profile fetched during the OAuth flow.

    ``avatar_url`` is percent-encoded so it survives a round trip through the
    JWT claims and the HTML form that later submits a candidacy.
    """

    user_id: str
    user_name: str
    avatar_url: str

    def __post_init__(self) -> None:
        self.avatar_url = quote(self.avatar_url)


@dataclass
class SubmitRequest:
    """A request to stand as a dora-person candidate.

    ``avatar_url`` arrives percent-encoded (see :class:`GitHubProfile`) and is
    decoded back to a plain URL before it reaches persistence.
    """

    user_name: str
    message: str
    avatar_url: str

    def __post_init__(self) -> None:
        self.avatar_url = unquote(self.avatar_url)


@dataclass
class Candidate:
    """A dora-person candidate as rendered on the vote page."""

    name: str
    message: str
    avatar_url: str
    count: int = 0

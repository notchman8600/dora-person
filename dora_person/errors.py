"""Domain-level error types shared across the persistence and service layers."""

from dataclasses import dataclass


@dataclass
class Error:
    """A recoverable failure returned by the persistence layer."""

    code: int
    message: str


class GitHubOAuthError(Exception):
    """Raised when the GitHub OAuth token exchange returns an error."""

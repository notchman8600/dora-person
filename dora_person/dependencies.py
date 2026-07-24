"""FastAPI dependency providers wiring settings, services and auth together."""

from functools import lru_cache
from typing import Any

import redis
from fastapi import Depends, HTTPException, Request, status
from jwt import ExpiredSignatureError, PyJWTError

from dora_person.config import Settings, get_settings
from dora_person.db.mysql import create_mysql_db
from dora_person.repositories.mysql_candidates import MySQLCandidateRepository
from dora_person.repositories.redis_votes import RedisVoteRepository
from dora_person.security import decode_access_token
from dora_person.services.github import GitHubGateway
from dora_person.services.votes import VoteService


@lru_cache
def _build_vote_service() -> VoteService:
    settings = get_settings()
    votes = RedisVoteRepository(redis.Redis(host=settings.redis_url, port=settings.redis_port, db=settings.redis_db))
    candidates = MySQLCandidateRepository(create_mysql_db(settings))
    return VoteService(votes=votes, candidates=candidates)


def get_vote_service() -> VoteService:
    """Provide the process-wide :class:`VoteService` (built lazily on first use)."""

    return _build_vote_service()


def get_github_gateway(settings: Settings = Depends(get_settings)) -> GitHubGateway:
    return GitHubGateway(settings)


def get_current_user(request: Request, settings: Settings = Depends(get_settings)) -> dict[str, Any]:
    """Decode the ``access_token`` cookie into its JWT claims.

    Replaces the token-parsing block that used to be duplicated across every
    protected route. The raised status codes are preserved so the existing
    exception handlers keep redirecting unauthenticated users to ``/login``.
    """

    token_str = request.cookies.get("access_token")
    if token_str is None:
        raise HTTPException(status_code=400, detail="Bad Request")

    parts = token_str.split(" ")
    if len(parts) != 2:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        return decode_access_token(parts[1], settings)
    except ExpiredSignatureError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err
    except PyJWTError as err:
        raise HTTPException(status_code=401, detail="Unauthorized") from err

"""Redis-backed storage of per-target vote counters."""

import redis

from dora_person.errors import Error


class RedisVoteRepository:
    """Stores one counter per ``target:voter`` pair.

    A single client is held for the lifetime of the repository; ``redis.Redis``
    manages its own connection pool internally.
    """

    def __init__(self, client: redis.Redis) -> None:
        self._client = client

    def record_vote(self, voter_id: str, target_id: str) -> Error | None:
        key = f"{target_id}:{voter_id}"
        before = int(self._client.get(key) or 0)
        self._client.incr(key)
        after = int(self._client.get(key))
        if before == after:
            return Error(code=500, message="failed to count record")
        return None

    def count_for_target(self, target_id: str) -> int:
        total = 0
        for key in self._client.keys(f"{target_id}:*"):
            total += int(self._client.get(key))
        return total

    def reset(self) -> bool:
        self._client.flushdb()
        return True

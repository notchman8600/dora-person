"""MySQL-backed storage of dora-person candidates."""

from dora_person.db.interface import DBInfraInterface
from dora_person.errors import Error

_INSERT_CANDIDATE = (
    "INSERT INTO dora_persons (user_name,dora_message,avatar_url) VALUES (?, ?, ?) "
    "ON DUPLICATE KEY UPDATE dora_message=?, avatar_url=?"
)
_SELECT_CANDIDATES = "SELECT user_name, dora_message, avatar_url FROM dora_persons order by created_at desc"


class MySQLCandidateRepository:
    """Persists candidacies and lists candidates ordered by recency."""

    def __init__(self, db: DBInfraInterface) -> None:
        self._db = db

    def upsert(self, user_name: str, message: str, avatar_url: str) -> Error | None:
        _, error = self._db.execute(_INSERT_CANDIDATE, user_name, message, avatar_url, message, avatar_url)
        return error

    def list_rows(self) -> tuple[list[tuple[str, str, str]], Error | None]:
        return self._db.query(_SELECT_CANDIDATES)

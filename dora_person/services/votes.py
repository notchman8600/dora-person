"""Vote domain logic sitting between the routers and the repositories."""

from dora_person.errors import Error
from dora_person.repositories.mysql_candidates import MySQLCandidateRepository
from dora_person.repositories.redis_votes import RedisVoteRepository
from dora_person.schemas import Candidate, SubmitRequest


class VoteService:
    def __init__(self, votes: RedisVoteRepository, candidates: MySQLCandidateRepository) -> None:
        self._votes = votes
        self._candidates = candidates

    def record_vote(self, voter_id: str, target_id: str) -> Error | None:
        return self._votes.record_vote(voter_id=voter_id, target_id=target_id)

    def reset(self) -> None:
        self._votes.reset()

    def submit_candidacy(self, request: SubmitRequest) -> Error | None:
        return self._candidates.upsert(
            user_name=request.user_name,
            message=request.message,
            avatar_url=request.avatar_url,
        )

    def list_candidates(self) -> list[Candidate]:
        """Return candidates enriched with vote counts, most-voted first."""

        rows, error = self._candidates.list_rows()
        if error is not None:
            return []
        candidates = [
            Candidate(
                name=name,
                message=message,
                avatar_url=avatar_url,
                count=self._votes.count_for_target(name),
            )
            for name, message, avatar_url in rows
        ]
        return sorted(candidates, key=lambda c: c.count, reverse=True)

from dora_person.errors import Error
from dora_person.schemas import SubmitRequest
from dora_person.services.votes import VoteService


class FakeVotes:
    def __init__(self, counts=None):
        self.counts = counts or {}
        self.recorded: list = []
        self.reset_called = False

    def record_vote(self, voter_id, target_id):
        self.recorded.append((voter_id, target_id))
        return None

    def count_for_target(self, target_id):
        return self.counts.get(target_id, 0)

    def reset(self):
        self.reset_called = True


class FakeCandidates:
    def __init__(self, rows=None, error=None):
        self.rows = rows or []
        self.error = error
        self.upserts: list = []

    def upsert(self, user_name, message, avatar_url):
        self.upserts.append((user_name, message, avatar_url))
        return None

    def list_rows(self):
        return self.rows, self.error


def test_list_candidates_sorted_by_count_desc():
    votes = FakeVotes(counts={"a": 1, "b": 3, "c": 2})
    candidates = FakeCandidates(rows=[("a", "ma", "ua"), ("b", "mb", "ub"), ("c", "mc", "uc")])
    service = VoteService(votes=votes, candidates=candidates)

    result = service.list_candidates()

    assert [c.name for c in result] == ["b", "c", "a"]
    assert [c.count for c in result] == [3, 2, 1]


def test_list_candidates_returns_empty_on_error():
    service = VoteService(votes=FakeVotes(), candidates=FakeCandidates(error=Error(code=500, message="boom")))

    assert service.list_candidates() == []


def test_submit_candidacy_delegates_to_repository():
    candidates = FakeCandidates()
    service = VoteService(votes=FakeVotes(), candidates=candidates)

    service.submit_candidacy(SubmitRequest(user_name="octocat", message="hi", avatar_url="https://a/x"))

    assert candidates.upserts == [("octocat", "hi", "https://a/x")]


def test_reset_delegates_to_repository():
    votes = FakeVotes()
    VoteService(votes=votes, candidates=FakeCandidates()).reset()

    assert votes.reset_called

import fakeredis

from dora_person.db.interface import DBInfraInterface
from dora_person.errors import Error
from dora_person.repositories.mysql_candidates import MySQLCandidateRepository
from dora_person.repositories.redis_votes import RedisVoteRepository


def test_redis_records_and_counts_votes():
    repo = RedisVoteRepository(fakeredis.FakeStrictRedis())

    assert repo.record_vote(voter_id="alice", target_id="bob") is None
    repo.record_vote(voter_id="carol", target_id="bob")

    assert repo.count_for_target("bob") == 2
    assert repo.count_for_target("nobody") == 0


def test_redis_reset_clears_counts():
    repo = RedisVoteRepository(fakeredis.FakeStrictRedis())
    repo.record_vote(voter_id="alice", target_id="bob")

    repo.reset()

    assert repo.count_for_target("bob") == 0


class FakeDB(DBInfraInterface):
    def __init__(self, rows=None, query_error=None, execute_error=None):
        self.rows = rows or []
        self.query_error = query_error
        self.execute_error = execute_error
        self.executed: list = []

    def query(self, statement, *args):
        return self.rows, self.query_error

    def execute(self, statement, *args):
        self.executed.append((statement, args))
        return len(args), self.execute_error


def test_candidate_upsert_passes_five_bound_params():
    db = FakeDB()
    repo = MySQLCandidateRepository(db)

    assert repo.upsert("octocat", "hi", "https://a/x") is None
    statement, args = db.executed[0]
    assert "ON DUPLICATE KEY UPDATE" in statement
    assert args == ("octocat", "hi", "https://a/x", "hi", "https://a/x")


def test_candidate_upsert_surfaces_error():
    repo = MySQLCandidateRepository(FakeDB(execute_error=Error(code=500, message="boom")))

    assert repo.upsert("octocat", "hi", "u").message == "boom"


def test_candidate_list_returns_rows():
    repo = MySQLCandidateRepository(FakeDB(rows=[("octocat", "hi", "u")]))

    rows, error = repo.list_rows()

    assert error is None
    assert rows == [("octocat", "hi", "u")]

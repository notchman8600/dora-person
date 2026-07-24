import pytest
from fastapi.testclient import TestClient

from dora_person.config import Settings, get_settings
from dora_person.dependencies import get_current_user, get_github_gateway, get_vote_service
from dora_person.main import create_app


@pytest.fixture
def settings() -> Settings:
    return Settings(
        secret_key="test-secret-key",
        client_id="test-client-id",
        client_secret="test-client-secret",
        redirect_url="https://example.test/auth",
        admin_github_name="notchman8600",
    )


class FakeVoteService:
    """In-memory stand-in for :class:`VoteService` used in route tests."""

    def __init__(self) -> None:
        self.candidates: list = []
        self.submitted: list = []
        self.votes: list = []
        self.reset_called = False
        self.submit_error = None
        self.vote_error = None

    def list_candidates(self):
        return self.candidates

    def submit_candidacy(self, request):
        self.submitted.append(request)
        return self.submit_error

    def record_vote(self, voter_id, target_id):
        self.votes.append((voter_id, target_id))
        return self.vote_error

    def reset(self):
        self.reset_called = True


@pytest.fixture
def fake_service() -> FakeVoteService:
    return FakeVoteService()


@pytest.fixture
def app(settings, fake_service):
    application = create_app()
    application.dependency_overrides[get_settings] = lambda: settings
    application.dependency_overrides[get_vote_service] = lambda: fake_service
    return application


@pytest.fixture
def client(app):
    return TestClient(app, raise_server_exceptions=False)


def login_as(app, github_name: str, avatar_url: str = "https://avatars.githubusercontent.com/u/1") -> None:
    """Override the auth dependency so routes see an authenticated user."""

    app.dependency_overrides[get_current_user] = lambda: {
        "github_name": github_name,
        "avatar_url": avatar_url,
        "github_id": 1,
    }


def set_gateway(app, gateway) -> None:
    app.dependency_overrides[get_github_gateway] = lambda: gateway

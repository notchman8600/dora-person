import respx
from fastapi.testclient import TestClient

from dora_person.schemas import Candidate
from dora_person.services.github import GitHubGateway
from tests.conftest import login_as, set_gateway


def test_index_page_renders(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "令和に蘇りし銅鑼パーソン" in response.text


def test_login_redirects_to_github(app, settings):
    set_gateway(app, GitHubGateway(settings))
    with TestClient(app) as client:
        response = client.get("/login", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"].startswith("https://github.com/login/oauth/authorize")


def test_vote_page_without_cookie_renders_error(client):
    # A missing cookie raises HTTPException(400); only 401s redirect to /login.
    response = client.get("/vote", follow_redirects=False)

    assert response.status_code == 500


def test_vote_page_with_invalid_token_redirects_to_login(client):
    response = client.get("/vote", cookies={"access_token": "garbage"}, follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/login"


def test_vote_page_renders_candidates(app, fake_service):
    fake_service.candidates = [Candidate(name="octocat", message="hi", avatar_url="u", count=3)]
    login_as(app, "octocat")
    with TestClient(app) as client:
        response = client.get("/vote")

    assert response.status_code == 200
    assert "octocat" in response.text
    assert "Your GitHub ID: octocat" in response.text


def test_submit_redirects_and_records(app, fake_service):
    login_as(app, "octocat")
    with TestClient(app) as client:
        response = client.post("/submit", data={"message": "go"}, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/vote"
    assert fake_service.submitted[0].user_name == "octocat"


def test_vote_redirects_and_records(app, fake_service):
    login_as(app, "voter")
    with TestClient(app) as client:
        response = client.post("/vote", data={"target_user_id": "octocat"}, follow_redirects=False)

    assert response.status_code == 303
    assert fake_service.votes == [("voter", "octocat")]


def test_reset_forbidden_for_non_admin(app, fake_service):
    login_as(app, "someone_else")
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/reset")

    assert response.status_code == 500  # HTTPException(403) is rendered via the error page
    assert fake_service.reset_called is False


def test_reset_allowed_for_admin(app, fake_service):
    login_as(app, "notchman8600")
    with TestClient(app) as client:
        response = client.get("/reset", follow_redirects=False)

    assert response.status_code == 303
    assert fake_service.reset_called is True


@respx.mock
def test_auth_sets_cookie_and_renders(app, settings):
    respx.post("https://github.com/login/oauth/access_token").mock(
        return_value=__import__("httpx").Response(200, json={"access_token": "gho"})
    )
    respx.get("https://api.github.com/user").mock(
        return_value=__import__("httpx").Response(200, json={"id": 1, "login": "octocat", "avatar_url": "https://a/x"})
    )
    set_gateway(app, GitHubGateway(settings))
    with TestClient(app) as client:
        response = client.get("/auth", params={"code": "abc"}, follow_redirects=False)

    assert response.status_code == 200
    set_cookie = response.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie
    assert "Bearer " in set_cookie

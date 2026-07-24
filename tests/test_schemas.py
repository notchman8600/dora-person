from dora_person.schemas import Candidate, GitHubProfile, SubmitRequest


def test_github_profile_percent_encodes_avatar():
    profile = GitHubProfile(user_id=1, user_name="octocat", avatar_url="https://a/x?y=1")

    assert profile.avatar_url == "https%3A//a/x%3Fy%3D1"


def test_submit_request_decodes_avatar():
    request = SubmitRequest(user_name="octocat", message="hi", avatar_url="https%3A//a/x%3Fy%3D1")

    assert request.avatar_url == "https://a/x?y=1"


def test_profile_to_submit_round_trip():
    profile = GitHubProfile(user_id=1, user_name="octocat", avatar_url="https://a/x")
    request = SubmitRequest(user_name=profile.user_name, message="hi", avatar_url=profile.avatar_url)

    assert request.avatar_url == "https://a/x"


def test_candidate_defaults_count_to_zero():
    assert Candidate(name="a", message="m", avatar_url="u").count == 0

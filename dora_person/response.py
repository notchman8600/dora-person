# Standard Library
from urllib.parse import quote


class GitHubProfileDto:
    user_id: str
    user_name: str
    avatar_url: str

    def __init__(self, user_id: str, user_name: str, avatar_url: str):
        self.user_id = user_id
        self.user_name = user_name
        self.avatar_url = quote(avatar_url)
        pass


class DoraPersonDto:
    name: str
    message: str
    avatar_url: str
    count: int

    def __init__(self, name: str, message: str, avatar_url: str, count: int = 0):
        self.name = name
        self.message = message
        self.avatar_url = avatar_url
        self.count = count
        pass

# Standard Library
import os

# Third Party Library
import httpx

# First Party Library
from dora_person.response import GitHubProfileDto
from dora_person.store import AccessCountStore


class DoraController:
    count_store: AccessCountStore

    def __init__(self):
        self.count_store = AccessCountStore(os.environ.get("REDIS_URL", "redis://redis:6379/0"))
        pass

    def store_access_count(self, request_user_id, target_user_id):
        self.count_store.store_record(request_user_id, target_user_id)
        pass

    def reset_count(self):
        self.count_store.reset_store()
        pass

    async def get_user_detail(self, user_id, access_token):
        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.github.com/user", headers={"Authorization": f"token {access_token}"})
        profile_data = r.json()
        print("response", profile_data)
        return GitHubProfileDto(user_id, profile_data["login"], profile_data["avatar_url"])

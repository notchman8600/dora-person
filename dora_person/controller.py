# Standard Library
import os
import sys
from http.client import HTTPException

# Third Party Library
import httpx

# First Party Library
from dora_person.error import Error
from dora_person.mysql.mysql_db import mysql_instance
from dora_person.request import SubmitDoraPersonRequestDto
from dora_person.response import DoraPersonDto, GitHubProfileDto
from dora_person.store import AccessCountStore


class DoraController:
    count_store: AccessCountStore

    def __init__(self):
        self.count_store = AccessCountStore(os.environ.get("REDIS_URL", "redis"), db_instance=mysql_instance)
        pass

    def store_vote_count(self, request_user_id, target_user_id) -> Error | None:
        err = self.count_store.store_record(request_user_id=request_user_id, target_user_id=target_user_id)
        return err

    def aggregate_vote_record(self, target_user_id) -> tuple[int, Error | None]:
        count, err = self.count_store.aggregate_vote_record(target_user_id=target_user_id)
        return count, err

    def reset_count(self):
        self.count_store.reset_store()
        pass

    def submit_dora_person(self, request: SubmitDoraPersonRequestDto):
        err = self.count_store.submit_dora_person(
            request_user_id=request.user_name, message=request.message, avatar_url=request.avatar_url
        )
        return err

    def get_dora_person_candidates(self) -> list[DoraPersonDto]:
        candidates, err = self.count_store.dora_person_candidates()
        response = [DoraPersonDto(name=c.name, message=c.message, avatar_url=c.avatar_url, count=c.count) for c in candidates]
        # テスト用
        # response.extend(
        #     [
        #         DoraPersonDto(name="test", message="test", avatar_url="https://avatars.githubusercontent.com/u/30828280?v=4")
        #         for i in range(100)
        #     ]
        # )
        # レスポンスデータを投票数順にソートする
        response = sorted(response, key=lambda x: x.count, reverse=True)
        return response

    async def get_user_detail(self, access_token) -> GitHubProfileDto:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.github.com/user", headers={"Authorization": f"token {access_token}"})
        profile_data = r.json()
        print("response", profile_data)
        return GitHubProfileDto(
            user_id=profile_data["id"], user_name=profile_data["login"], avatar_url=profile_data["avatar_url"]
        )

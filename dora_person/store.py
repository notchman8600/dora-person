# Third Party Library
import redis

# First Party Library
from dora_person.error import Error
from dora_person.model import DoraPerson
from dora_person.mysql.mysql_db import MySqlDB


class AccessCountStore:
    redis_url: str
    db: MySqlDB

    def __init__(self, redis_url: str, db_instance: MySqlDB):
        self.redis_url = redis_url
        self.db = db_instance

    def store_record(self, request_user_id: str, target_user_id: str) -> Error | None:
        r = redis.Redis(host=self.redis_url, port=6379, db=0)
        key = f"{target_user_id}:{request_user_id}"
        b_count = r.get(key)
        # キーが存在しないときはNoneとなるので0を代入する
        if b_count is None:
            b_count = 0
        # bytes -> int
        b_count = int(b_count)
        r.incr(key)
        a_count = int(r.get(key))
        if b_count == a_count:
            return Error(code=500, message="failed to count record")

        return None

    def aggregate_vote_record(self, target_user_id: str) -> tuple[int, Error | None]:
        r = redis.Redis(host=self.redis_url, port=6379, db=0)
        keys = r.keys(f"{target_user_id}:*")
        total = 0
        for key in keys:
            # 各キーの値（カウンタ）を取得して合計する
            total += int(r.get(key))
        return total, None

    def reset_store(self):
        r = redis.Redis(host=self.redis_url, port=6379, db=0)
        r.flushdb()
        return True

    def submit_dora_person(self, request_user_id: str, message: str, avatar_url: str) -> Error | None:
        stmt = """INSERT INTO dora_persons (user_name,dora_message,avatar_url) VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE dora_message=?, avatar_url=?"""
        _, msg = self.db.execute(
            stmt,
            *(request_user_id, message, avatar_url, message, avatar_url),
        )
        return msg

    def dora_person_candidates(self):
        stmt = "SELECT user_name, dora_message, avatar_url FROM dora_persons order by created_at desc"
        result, msg = self.db.query(stmt)
        if msg is not None:
            return [], msg
        result = [DoraPerson(row[0], row[1], row[2], self.__count_by_user_id(row[0])) for row in result]
        return result, None

    def __count_by_user_id(self, user_id) -> int:
        r = redis.Redis(host=self.redis_url, port=6379, db=0)
        keys = r.keys(f"{user_id}:*")
        total = 0
        for key in keys:
            # 各キーの値（カウンタ）を取得して合計する
            total += int(r.get(key))
        return total

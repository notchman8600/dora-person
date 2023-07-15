# Third Party Library
import redis


class AccessCountStore:
    redis_url: str

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        pass

    def store_record(self, request_user_id: str, target_user_id: str):
        r = redis.Redis(host=self.redis_url, port=6379, db=0)
        key = f"{target_user_id}:{request_user_id}"
        r.incr(key)

    def reset_store(self):
        r = redis.Redis(host=self.redis_url, port=6379, db=0)
        r.flushdb()

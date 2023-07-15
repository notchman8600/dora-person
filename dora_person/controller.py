# Standard Library
import os

# First Party Library
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

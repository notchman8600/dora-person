"""Centralised application configuration.

All environment access goes through :class:`Settings` so that the rest of the
code never touches ``os.environ`` directly. This keeps configuration testable
and documents every knob the application understands in a single place.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # GitHub OAuth application credentials.
    client_id: str | None = None
    client_secret: str | None = None
    redirect_url: str | None = None

    # JWT / session settings. ``secret_key`` has no default on purpose: the key
    # used to sign session tokens must be supplied via the environment so it is
    # never a value that is public in source control.
    secret_key: str | None = None
    jwt_algorithm: str = "HS256"
    token_expire_minutes: int = 15
    admin_github_name: str = "notchman8600"

    # Redis vote store. ``redis_url`` is used as a hostname (see RedisVoteRepository).
    redis_url: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    # MySQL candidate store.
    mysql_db_host: str | None = None
    mysql_db_user: str | None = None
    mysql_db_pass: str | None = None
    mysql_db_name: str | None = None
    mysql_db_port: str | None = None
    mysql_pool_size: int = 30
    mysql_pool_name: str = "n4u-mysql"

    @property
    def signing_key(self) -> str:
        """Return the JWT signing key, failing loudly when it is missing."""

        if not self.secret_key:
            raise RuntimeError("SECRET_KEY environment variable must be set to sign session tokens")
        return self.secret_key


@lru_cache
def get_settings() -> Settings:
    """Return a process-wide cached :class:`Settings` instance."""

    return Settings()

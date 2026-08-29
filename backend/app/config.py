from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://taskuser:taskpass@localhost:5432/tasks"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173"
    queue_name: str = "tasks"
    worker_id: str = "worker-1"
    worker_metrics_port: int = 8001

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

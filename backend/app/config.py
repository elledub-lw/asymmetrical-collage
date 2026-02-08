from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Required
    api_key: str
    github_token: str
    github_repo: str
    database_url: str = "/data/blog.db"

    # Email fallback (optional)
    gmail_address: str = ""
    gmail_app_password: str = ""

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()

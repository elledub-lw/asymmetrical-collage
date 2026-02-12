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

    # Market Watch Newsletter settings
    perplexity_api_key: str = ""
    anthropic_api_key: str = ""
    resend_api_key: str = ""
    digest_to_email: str = ""
    digest_from_email: str = ""

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()

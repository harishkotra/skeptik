from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_name: str = "Skeptik Newsroom API"
    app_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    database_url: str = "sqlite:///./skeptik.db"

    featherless_api_key: str = ""
    featherless_base_url: str = "https://api.featherless.ai/v1"
    featherless_model: str = "moonshotai/Kimi-K2.5"

    tavily_api_key: str = ""
    tavily_api_url: str = "https://api.tavily.com"

    brightdata_api_key: str = ""
    brightdata_api_url: str = "https://api.brightdata.com/request"
    brightdata_zone: str = ""

    virlo_api_key: str = ""
    virlo_api_url: str = "https://api.virlo.ai/v1/trends/digest"

    newsroom_autopilot_enabled: bool = True
    newsroom_autopilot_seconds: int = 900
    newsroom_default_region: str = "global"
    newsroom_min_sources: int = 3
    newsroom_max_false_claims: int = 0
    newsroom_max_uncertain_ratio: float = Field(default=0.34, ge=0, le=1)
    newsroom_max_skeptic_score: float = Field(default=0.62, ge=0, le=1)
    newsroom_target_article_count: int = 8


@lru_cache
def get_settings() -> Settings:
    return Settings()

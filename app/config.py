"""Pydantic settings loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings. Loaded from env and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database — two modes: Supabase (remote) or Local (Docker)
    # Resolver: DATABASE_URL = SUPABASE_DB_URL if set, else LOCAL_DB_URL
    local_db_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_agents"
    supabase_db_url: str | None = None

    @computed_field
    @property
    def database_url(self) -> str:
        """Resolved DB URL: Supabase if set, otherwise Local."""
        return self.supabase_db_url or self.local_db_url

    @computed_field
    @property
    def database_use_ssl(self) -> bool:
        """True when using Supabase (SSL required for remote Postgres)."""
        return self.supabase_db_url is not None

    # Optional Supabase API (Auth, Storage, etc.)
    supabase_url: str | None = None
    supabase_service_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()

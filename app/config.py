"""Pydantic settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env next to project root (parent of app/) so it loads regardless of cwd
_env_path = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Application settings. Loaded from env and .env file."""

    model_config = SettingsConfigDict(
        env_file=_env_path if _env_path.exists() else ".env",
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

    # OpenAI / ChatGPT (set OPENAI_API_KEY in .env; never commit the key)
    openai_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()

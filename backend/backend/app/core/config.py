"""Application configuration.

All configuration is loaded from environment variables via pydantic-settings.
Nothing in this codebase should ever read `os.environ` directly, and no
secret should ever appear as a literal in source code -- everything routes
through this module so there is exactly one place to audit.

`get_settings()` is cached so settings are parsed once per process and
handed out as a singleton via FastAPI's dependency injection.
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from pydantic import Field, PostgresDsn, RedisDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "Appex Asset Suite"
    environment: Environment = Environment.LOCAL
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # --- CORS ---
    # Comma-separated in the environment, e.g. CORS_ORIGINS=https://a.com,https://b.com
    cors_origins: list[str] = Field(default_factory=list)

    # --- Database ---
    # The application connects with a *restricted* role that has row-level
    # security enforced against it. Migrations use a separate, more
    # privileged role configured independently (see infrastructure/db).
    database_url: PostgresDsn

    # --- Cache ---
    redis_url: RedisDsn

    # --- Auth / JWT ---
    # Session tokens issued by our own backend after Telegram initData
    # verification. HS256 is sufficient for a single-service MVP; revisit
    # if session tokens ever need to be verified by another service.
    jwt_secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # --- Telegram ---
    # MVP uses a single shared bot (see TelegramBotProvider). This value is
    # the default/fallback bot token; a per-tenant provider implementation
    # would source tokens from the tenant registry instead of this field.
    telegram_bot_token: SecretStr

    # --- AI module ---
    # Base URL of the ai-module service. The concrete AIModulePort
    # implementation calling this URL is added once the module's contract
    # is finalized; the setting is defined now so it never needs to be
    # hardcoded later.
    ai_module_base_url: str = "http://ai-module:8100"

    # --- Logging ---
    log_level: str = "INFO"
    log_json: bool = True

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_local(self) -> bool:
        return self.environment == Environment.LOCAL

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide Settings singleton.

    Cached so environment variables are parsed exactly once. Tests that
    need different settings should call `get_settings.cache_clear()` and
    override environment variables, or use FastAPI's dependency_overrides.
    """
    return Settings()  # type: ignore[call-arg]  # values come from the environment

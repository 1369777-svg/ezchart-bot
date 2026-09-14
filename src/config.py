"""
EZChart — configuration loader.

Loads settings from environment variables (see .env.example).
Uses pydantic-settings for type safety and validation.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # === Telegram ===
    telegram_token: str = Field(
        ...,
        alias="TELEGRAM_TOKEN",
        description="Telegram Bot API token from @BotFather",
    )

    # === Gemini ===
    gemini_api_key: str = Field(
        ...,
        alias="GEMINI_API_KEY",
        description="Google Gemini API key from AI Studio",
    )
    gemini_model: str = Field(
        default="gemini-2.0-flash",
        alias="GEMINI_MODEL",
        description="Gemini model name",
    )

    # === App ===
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
        description="Logging level: DEBUG / INFO / WARNING / ERROR",
    )
    rate_limit_sec: int = Field(
        default=10,
        alias="RATE_LIMIT_SEC",
        description="Anti-spam window in seconds per user",
        ge=1,
        le=300,
    )

    @property
    def is_debug(self) -> bool:
        return self.log_level.upper() == "DEBUG"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings accessor."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
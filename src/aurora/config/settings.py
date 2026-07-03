"""Configuration settings, loaded from environment variables or a .env file."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    discord_token: str = Field(description="Discord bot token")
    guild_id: int = Field(description="The guild (server) id")
    logs_channel_id: int | None = Field(
        default=None,
        description="Channel Aurora posts logs to. `None` means it is disabled.",
    )
    general_log_level: str = Field(
        default="INFO",
        description="General log level.",
    )
    log_level: str = Field(default="DEBUG", description="Log level of Aurora.")

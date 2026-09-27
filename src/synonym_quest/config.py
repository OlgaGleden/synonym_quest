"""Настройки приложения Synonym Quest.

Читаются из .env (см. .env.example). Единая точка доступа — объект `settings`.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Мессенджер MAX ---
    bot_token: str = Field(..., alias="BOT_TOKEN")

    # --- Инфраструктура ---
    database_url: str = Field(..., alias="DATABASE_URL")
    redis_url: str = Field(..., alias="REDIS_URL")

    # --- Логирование и режим работы ---
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    use_webhook: bool = Field(False, alias="USE_WEBHOOK")
    webhook_url: str = Field("", alias="WEBHOOK_URL")


settings = Settings()

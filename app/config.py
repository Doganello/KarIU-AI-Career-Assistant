from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # Основные настройки
    DATABASE_URL: str
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    ANTHROPIC_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT настройки
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 день

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
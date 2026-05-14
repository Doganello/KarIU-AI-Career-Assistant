from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json


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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # CORS - парсим из строки если пришло как строка
    CORS_ORIGINS_raw: str = '["http://localhost:5173","http://127.0.0.1:5173"]'

    @property
    def CORS_ORIGINS(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS_raw, str):
            return json.loads(self.CORS_ORIGINS_raw)
        return self.CORS_ORIGINS_raw

    # Дополнительные настройки
    COOKIE_SECURE: bool = False
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "lax"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
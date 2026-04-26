from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    ANTHROPIC_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 день

    class Config:
        env_file = ".env"

settings = Settings()
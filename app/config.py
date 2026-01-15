# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Default to a local file for dev, but Docker will override this
    DATABASE_URL: str = "sqlite:///./app.db"
    WEBHOOK_SECRET: str
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
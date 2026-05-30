import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SentinelMind"
    VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    API_KEY_SECRET: str = os.getenv("API_KEY_SECRET", "dev-secret-change-in-prod")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sentinelmind.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    PAYSTACK_SECRET_KEY: str = os.getenv("PAYSTACK_SECRET_KEY", "")
    PAYSTACK_WEBHOOK_SECRET: str = os.getenv("PAYSTACK_WEBHOOK_SECRET", "")
    MAX_FILE_SIZE_MB: int = 10
    CONFIDENCE_THRESHOLD: float = 0.75

    class Config:
        env_file = ".env"

settings = Settings()

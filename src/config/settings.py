from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    TWITTER_API_KEY: str
    TWITTER_API_SECRET: str
    TWITTER_ACCESS_TOKEN: str
    TWITTER_ACCESS_TOKEN_SECRET: str
    TWITTER_BEARER_TOKEN: str | None = None
    COINGECKO_API_KEY: str

    # Feature flags
    ENABLE_IMAGE_GENERATION: bool = True

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Scheduler Settings
    SCHEDULE_TIMES: list[str] = ["10:00", "15:00", "20:00"]

    # Timezone Settings
    LOCAL_TIMEZONE: str = "Australia/Melbourne"
    TARGET_TIMEZONE: str = "America/New_York"


class Config:
    env_file = ".env"
    extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# config/settings.py

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    # Database Configuration
    MONGODB_URL: str
    REDIS_URL: str

    # Security Configuration
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # External API Keys
    OPENWEATHER_API_KEY: Optional[str] = ""
    GOOGLE_MAPS_API_KEY: Optional[str] = ""
    ELEVATION_API_KEY: Optional[str] = ""

    # Application Configuration
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    # ---------------------------
    # Validators for reused fields
    # ---------------------------

    @field_validator('DEBUG', mode="before")
    @classmethod
    def set_debug(cls, v):
        if isinstance(v, bool):
            return v
        return str(v).lower() in ('true', '1', 'yes')

    @field_validator('MONGODB_URL')
    @classmethod
    def validate_mongodb_url(cls, v):
        if not v:
            raise ValueError('MONGODB_URL is required')
        return v

    @field_validator('REDIS_URL')
    @classmethod
    def validate_redis_url(cls, v):
        if not v:
            raise ValueError('REDIS_URL is required')
        return v

    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v

    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


# Global settings instance
settings = Settings()

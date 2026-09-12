from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Core Application Settings
    PROJECT_NAME: str = "XEROX"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Security & Auth
    SECRET_KEY: str = "xerox_development_secret_key_change_in_production_32_chars_min"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database (PostgreSQL primary, fallback to SQLite for local development/testing)
    DATABASE_URL: str = "sqlite+aiosqlite:///./xerox.db"

    # Cache (Redis primary, fallback to in-memory/fakeredis)
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 86400  # 24 hours

    # External APIs
    VIRUSTOTAL_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Workers & Auditing
    ASYNC_AUDIT_LOGGING: bool = True
    MAX_WORKERS: int = 4


settings = Settings()

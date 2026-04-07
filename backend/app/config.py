from pydantic_settings import BaseSettings
from typing import List
import secrets


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Science and Innovation Journal"
    APP_URL: str = "https://yourjournal.com"
    DEBUG: bool = False
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    # Database
    DATABASE_URL: str
    SYNC_DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT
    SECRET_KEY: str = secrets.token_urlsafe(64)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Mail
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@example.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "Science and Innovation Journal"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        # Env vars are injected by docker-compose env_file directive (single .env at project root)
        # Local fallback: .env file in current working directory
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()

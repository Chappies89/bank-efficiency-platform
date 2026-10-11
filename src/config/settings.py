"""Application settings loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from .env or environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql://bankuser:bankpass@localhost:5432/bank_efficiency"
    mlflow_tracking_uri: str = "http://localhost:5000"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    environment: str = "development"


settings = Settings()

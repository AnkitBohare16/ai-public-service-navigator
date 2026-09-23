from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Public-Service Information Navigator"
    app_env: str = "development"

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    database_url: str = (
        "postgresql://postgres:postgres@localhost:5432/"
        "public_service_navigator"
    )

    llm_api_key: str | None = None
    embedding_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
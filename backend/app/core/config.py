from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    test_database_url: str | None = None
    jwt_secret_key: str
    jwt_algorithm: str = Field(default="HS256", pattern=r"^HS(256|384|512)$")
    access_token_expire_minutes: int = Field(default=30, gt=0, le=1440)
    cors_origins: str = "http://localhost:5173"
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.environment.lower() not in {"development", "test"}:
            if len(self.jwt_secret_key) < 32 or any(
                marker in self.jwt_secret_key.lower() for marker in ("replace-with", "change-me", "placeholder")
            ):
                raise ValueError("JWT_SECRET_KEY must be a random secret of at least 32 characters outside development")
            if "*" in self.cors_origin_list:
                raise ValueError("wildcard CORS origins are not allowed outside development")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

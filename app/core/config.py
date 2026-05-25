from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TANAW API"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tanaw_local"
    jwt_secret_key: str = "change-this-local-development-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8
    default_it_username: str = "default@email.tanaw"
    default_it_password: str = "default"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"
    geocoder_provider: str = "nominatim"
    geocoder_api_key: str | None = None
    geocoder_base_url: str | None = None
    geocoder_user_agent: str = "TANAW/1.0 local-development"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

from functools import lru_cache
from typing import Any

from pydantic import BaseSettings, SecretStr


class BaseAppSettings(BaseSettings):
    class Config:
        env_file = "../.env"


class AppSettings(BaseAppSettings):
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = 'FastAPI-Blog'
    decription: str = "Example blog"
    version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    max_connection_count: int = 10
    min_connection_count: int = 10
    postgres_user: str
    postgres_password: str
    postgres_database: str
    postgres_host: str
    postgres_port: str

    access_secret_key: SecretStr
    refresh_secret_key: SecretStr

    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7

    jwt_algorithm: str = "HS256"

    allowed_hosts: list[str] = ["*"]

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        return {
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "description": self.decription,
            "version": self.version,
        }


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()

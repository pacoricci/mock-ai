from pathlib import Path
from typing import Annotated, Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class UvicornSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="UVICORN_", env_file=".env", extra="allow"
    )

    host: str = "0.0.0.0"
    port: int = 5001
    reload: bool = False
    root_path: str = ""
    proxy_headers: bool = True
    timeout_keep_alive: int = 60
    ssl_certfile: Path | None = None
    ssl_keyfile: Path | None = None
    ssl_keyfile_password: str | None = None
    workers: int | None = None


uvicorn_settings = UvicornSettings()


class AuthSettings(BaseSettings):
    """Authentication configuration."""

    model_config = SettingsConfigDict(
        env_prefix="AUTH_", env_file=".env", extra="allow"
    )

    bearer_tokens: Annotated[list[str], NoDecode]

    @field_validator("bearer_tokens", mode="before")
    @classmethod
    def parse_comma_separated(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v


auth_settings = AuthSettings()

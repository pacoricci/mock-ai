from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


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

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 12000
    root_dir: Path = Path.home()
    auth_enabled: bool = False
    auth_username: str = "admin"
    auth_password: str = ""
    allow_delete: bool = False
    max_upload_size: int = 10 * 1024**3  # 10GB
    chunk_size: int = 1024 * 1024  # 1MB

    model_config = SettingsConfigDict(env_prefix="LFS_", env_file=".env", extra="ignore")


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

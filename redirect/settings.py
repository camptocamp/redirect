"""Application settings using pydantic-settings."""

from typing import Annotated

from anyio import Path
from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _to_path(value: str | Path) -> Path:
    return Path(value) if isinstance(value, str) else value


_Path = Annotated[Path, BeforeValidator(_to_path)]


class Settings(BaseSettings):  # pylint: disable=too-few-public-methods
    """Redirect application settings."""

    model_config = SettingsConfigDict(env_prefix="REDIRECT__")

    redirect_hosts: _Path = Path("/etc/redirect/hosts.yaml")
    redirect_param: str = "came_from"
    log_level: str = "INFO"


settings = Settings()

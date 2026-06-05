import os
from pathlib import Path

from pydantic_settings import BaseSettings


def _find_env_file() -> str:
    """Search for .env in CWD first, then in parent directory (project root)."""
    candidates = [
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return ".env"


class Settings(BaseSettings):
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"

    database_url: str = "sqlite:///./speakcoach.db"

    model_config = {
        "env_file": _find_env_file(),
        "env_file_encoding": "utf-8",
    }


settings = Settings()

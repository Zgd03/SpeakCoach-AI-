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
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    database_url: str = "sqlite:///./speakcoach.db"

    model_config = {
        "env_file": _find_env_file(),
        "env_file_encoding": "utf-8",
    }

    @property
    def effective_api_url(self) -> str:
        """Get the full chat completions URL, handling optional /v1 prefix."""
        base = self.deepseek_base_url.rstrip("/")
        if base.endswith("/v1"):
            return f"{base}/chat/completions"
        return f"{base}/v1/chat/completions"


settings = Settings()

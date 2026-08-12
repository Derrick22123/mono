"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    openai_base_url: str
    agent_os_port: int
    web_dist_path: Path
    api_version: str
    cors_origins: list[str]
    max_message_length: int = 4000


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def get_settings() -> Settings:
    """Load settings from environment with repo-relative defaults."""
    port = int(os.getenv("AGENT_OS_PORT", "7777"))
    cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    cors_origins = [origin.strip() for origin in cors_raw.split(",") if origin.strip()]

    dist_override = os.getenv("WEB_DIST_PATH")
    web_dist_path = Path(dist_override) if dist_override else _repo_root() / "apps" / "web" / "dist"

    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "deepseek-v4-flash"),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com").rstrip("/"),
        agent_os_port=port,
        web_dist_path=web_dist_path,
        api_version="1.0.0",
        cors_origins=cors_origins,
    )

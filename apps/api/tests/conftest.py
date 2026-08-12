"""Shared pytest fixtures."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from agno.agent import Agent
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.main import build_app


@pytest.fixture
def test_settings(tmp_path) -> Settings:
    return Settings(
        openai_api_key="sk-test-key",
        openai_model="deepseek-v4-flash",
        openai_base_url="https://api.deepseek.com",
        agent_os_port=7777,
        web_dist_path=tmp_path / "dist",
        api_version="1.0.0",
        cors_origins=["http://localhost:5173"],
    )


@pytest.fixture
def settings_factory(tmp_path):
    def _make(*, api_key: str | None = "sk-test123") -> Settings:
        return Settings(
            openai_api_key=api_key,
            openai_model="deepseek-v4-flash",
            openai_base_url="https://api.deepseek.com",
            agent_os_port=7777,
            web_dist_path=tmp_path / "dist",
            api_version="1.0.0",
            cors_origins=["http://localhost:5173"],
        )

    return _make


@pytest.fixture
def mock_agent() -> Agent:
    agent = MagicMock(spec=Agent)
    agent.name = "chat"

    async def fake_stream(*args: Any, **kwargs: Any) -> AsyncIterator[Any]:
        yield MagicMock(content="測試回覆")

    agent.arun = AsyncMock(side_effect=fake_stream)
    return agent


@pytest.fixture
def app(test_settings: Settings, mock_agent: Agent):
    return build_app(settings=test_settings, agent=mock_agent)


@pytest.fixture
async def async_client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def override_openai_key(monkeypatch: pytest.MonkeyPatch):
    def _apply(key: str | None) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", key or "")

    return _apply

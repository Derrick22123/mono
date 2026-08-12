"""Integration tests for GET /v1/health."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import build_app


@pytest.mark.asyncio
async def test_health_missing_credentials(settings_factory):
    app = build_app(settings=settings_factory(api_key=None))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["checks"]["model_credentials"] == "missing"
    assert payload["checks"]["model_reachable"] == "skipped"


@pytest.mark.asyncio
async def test_health_healthy_with_reachable_model(settings_factory):
    app = build_app(settings=settings_factory())

    with patch("app.health.probe_model_reachable", new=AsyncMock(return_value="ok")):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["checks"]["model_credentials"] == "ok"
    assert payload["checks"]["model_reachable"] == "ok"

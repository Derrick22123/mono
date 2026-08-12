"""Integration tests for AG-UI streaming boundary."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from tests.helpers import agui_run_body

from app.main import build_app


@pytest.mark.asyncio
async def test_agui_stream_emits_text_content_events(settings_factory):
    async def fake_run_entity(entity, run_input, user_id=None):  # noqa: ANN001
        from ag_ui.core import EventType, RunFinishedEvent, TextMessageContentEvent

        yield TextMessageContentEvent(
            type=EventType.TEXT_MESSAGE_CONTENT,
            message_id="assistant-1",
            delta="你好",
        )
        yield RunFinishedEvent(
            type=EventType.RUN_FINISHED,
            thread_id=run_input.thread_id,
            run_id=run_input.run_id,
        )

    app = build_app(settings=settings_factory())

    body = agui_run_body(
        thread_id="thread-1",
        run_id="run-1",
        messages=[{"role": "user", "content": "你好"}],
    )

    with patch("agno.os.interfaces.agui.router.run_entity", new=fake_run_entity):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/agui", json=body)

    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
    assert "TEXT_MESSAGE_CONTENT" in response.text
    assert "你好" in response.text


@pytest.mark.asyncio
async def test_agui_returns_503_when_credentials_missing(settings_factory):
    app = build_app(settings=settings_factory(api_key=None))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/agui",
            json=agui_run_body(
                thread_id="t1",
                run_id="r1",
                messages=[{"role": "user", "content": "hi"}],
            ),
        )

    assert response.status_code == 503
    payload = response.json()
    assert payload["code"] == "MODEL_CREDENTIALS_MISSING"

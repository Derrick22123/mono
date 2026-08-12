"""Integration tests for AG-UI multi-turn history (FR-004a)."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from tests.helpers import agui_run_body

from app.main import build_app


@pytest.mark.asyncio
async def test_agui_receives_full_message_history_on_second_turn(settings_factory):
    captured_messages: list[list[Any]] = []

    async def fake_run_entity(entity, run_input, user_id=None):  # noqa: ANN001
        captured_messages.append(list(run_input.messages or []))
        from ag_ui.core import EventType, RunFinishedEvent, TextMessageContentEvent

        yield TextMessageContentEvent(
            type=EventType.TEXT_MESSAGE_CONTENT,
            message_id="m1",
            delta="好",
        )
        yield RunFinishedEvent(
            type=EventType.RUN_FINISHED,
            thread_id=run_input.thread_id,
            run_id=run_input.run_id,
        )

    app = build_app(settings=settings_factory())

    first_body = agui_run_body(
        thread_id="t1",
        run_id="r1",
        messages=[{"role": "user", "content": "第一句"}],
    )
    second_body = agui_run_body(
        thread_id="t1",
        run_id="r2",
        messages=[
            {"role": "user", "content": "第一句"},
            {"role": "assistant", "content": "回覆一"},
            {"role": "user", "content": "第二句"},
        ],
    )

    with patch("agno.os.interfaces.agui.router.run_entity", new=fake_run_entity):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            await client.post("/agui", json=first_body)
            await client.post("/agui", json=second_body)

    assert len(captured_messages) == 2
    assert len(captured_messages[1]) >= 3

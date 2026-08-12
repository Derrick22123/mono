"""Test helpers for AG-UI request payloads."""

from __future__ import annotations

from typing import Any


def agui_run_body(
    *,
    thread_id: str,
    run_id: str,
    messages: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a valid RunAgentInput JSON body for integration tests."""
    normalized_messages: list[dict[str, Any]] = []
    for index, message in enumerate(messages):
        role = message["role"]
        normalized_messages.append(
            {
                "id": message.get("id", f"m-{index}"),
                "role": role,
                "content": message.get("content", ""),
            }
        )

    return {
        "threadId": thread_id,
        "runId": run_id,
        "state": {},
        "messages": normalized_messages,
        "tools": [],
        "context": [],
        "forwardedProps": {},
    }

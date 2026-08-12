"""Request validation helpers for AG-UI chat input."""

from __future__ import annotations

from typing import Any

MAX_MESSAGE_CONTENT_LENGTH = 4000


def validate_messages_content(
    messages: list[Any],
    *,
    max_length: int = MAX_MESSAGE_CONTENT_LENGTH,
) -> str | None:
    """Return an error message when any message content exceeds the limit."""
    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if isinstance(content, str) and len(content) > max_length:
            return f"messages[{index}].content exceeds {max_length} characters"
    return None

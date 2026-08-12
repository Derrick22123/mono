"""Validation unit tests."""

from app.validation import validate_messages_content


def test_validate_messages_content_within_limit():
    messages = [{"role": "user", "content": "hello"}]
    assert validate_messages_content(messages) is None


def test_validate_messages_content_exceeds_limit():
    messages = [{"role": "user", "content": "x" * 4001}]
    assert validate_messages_content(messages) is not None

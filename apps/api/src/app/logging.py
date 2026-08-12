"""Structured JSON logging helpers."""

from __future__ import annotations

import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


class JsonFormatter(logging.Formatter):
    """Emit one JSON object per log line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname.lower(),
            "event": getattr(record, "event", record.getMessage()),
            "message": record.getMessage(),
        }
        request_id = request_id_ctx.get()
        if request_id:
            payload["request_id"] = request_id
        for key in ("method", "path", "status_code", "duration_ms"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def new_request_id() -> str:
    return str(uuid.uuid4())


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    extra = {"event": event, **fields}
    logger.info(event, extra=extra)

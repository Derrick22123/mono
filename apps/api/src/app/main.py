"""Agno AgentOS application entrypoint."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from agno.agent import Agent
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.agent import create_agent
from app.config import Settings, get_settings
from app.health import create_health_router
from app.logging import configure_logging, get_logger, log_event, new_request_id, request_id_ctx
from app.validation import validate_messages_content

configure_logging()
logger = get_logger("mono.api")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
        request_id = new_request_id()
        token = request_id_ctx.set(request_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            log_event(
                logger,
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
            )
            raise
        finally:
            request_id_ctx.reset(token)

        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        log_event(
            logger,
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        response.headers["X-Request-Id"] = request_id
        return response


class AguiGuardMiddleware(BaseHTTPMiddleware):
    """Reject /agui requests before SSE when credentials or payload are invalid."""

    def __init__(self, app: Any, settings: Settings) -> None:
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
        if request.method == "POST" and request.url.path.rstrip("/") == "/agui":
            api_key = self.settings.openai_api_key
            if not api_key or not api_key.strip():
                return JSONResponse(
                    status_code=503,
                    content={
                        "code": "MODEL_CREDENTIALS_MISSING",
                        "message": "OPENAI_API_KEY 未設定，無法開始對話。",
                    },
                )

            try:
                body = await request.body()
            except Exception:
                return JSONResponse(
                    status_code=400,
                    content={"code": "INVALID_REQUEST", "message": "無法讀取請求內容。"},
                )

            try:
                payload = json.loads(body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                return JSONResponse(
                    status_code=400,
                    content={"code": "INVALID_JSON", "message": "請求格式不正確。"},
                )

            messages = payload.get("messages", [])
            if not isinstance(messages, list):
                return JSONResponse(
                    status_code=400,
                    content={"code": "INVALID_MESSAGES", "message": "messages 必須為陣列。"},
                )

            validation_error = validate_messages_content(
                messages,
                max_length=self.settings.max_message_length,
            )
            if validation_error:
                return JSONResponse(
                    status_code=400,
                    content={
                        "code": "MESSAGE_TOO_LONG",
                        "message": f"訊息長度不可超過 {self.settings.max_message_length} 字元。",
                    },
                )

            async def receive() -> dict[str, Any]:
                return {"type": "http.request", "body": body, "more_body": False}

            request = Request(request.scope, receive)

        return await call_next(request)


def mount_static_dist(app: FastAPI, dist_path: Path) -> None:
    if dist_path.is_dir():
        app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="spa")


def build_app(
    settings: Settings | None = None,
    agent: Agent | None = None,
    *,
    mount_static: bool = False,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    chat_agent = agent or create_agent(
        api_key=resolved_settings.openai_api_key,
        model_id=resolved_settings.openai_model,
    )

    agent_os = AgentOS(
        agents=[chat_agent],
        interfaces=[AGUI(agent=chat_agent)],
        tracing=False,
    )
    app = agent_os.get_app()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(AguiGuardMiddleware, settings=resolved_settings)
    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(create_health_router(resolved_settings))

    if mount_static or resolved_settings.web_dist_path.is_dir():
        mount_static_dist(app, resolved_settings.web_dist_path)

    return app


app = build_app()

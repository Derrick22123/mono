"""Project-owned readiness endpoint matching health.openapi.yaml."""

from __future__ import annotations

import re
from typing import Literal

import httpx
from fastapi import APIRouter

from app.config import Settings, get_settings

HealthStatus = Literal["healthy", "degraded"]
CredentialStatus = Literal["ok", "missing", "invalid"]
ReachabilityStatus = Literal["ok", "failed", "skipped"]

API_KEY_PATTERN = re.compile(r"^sk-[A-Za-z0-9_-]+$")


def derive_model_credentials(api_key: str | None) -> CredentialStatus:
    if api_key is None or not api_key.strip():
        return "missing"
    if not API_KEY_PATTERN.match(api_key.strip()):
        return "invalid"
    return "ok"


def derive_overall_status(
    *,
    model_credentials: CredentialStatus,
    model_reachable: ReachabilityStatus,
) -> HealthStatus:
    if model_credentials != "ok":
        return "degraded"
    if model_reachable == "failed":
        return "degraded"
    return "healthy"


async def probe_model_reachable(
    *,
    api_key: str,
    model: str,
    client: httpx.AsyncClient | None = None,
) -> ReachabilityStatus:
    """Perform a lightweight OpenAI models request to verify credentials."""
    owns_client = client is None
    http_client = client or httpx.AsyncClient(timeout=5.0)
    try:
        response = await http_client.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        if response.status_code == 401:
            return "failed"
        if response.status_code >= 400:
            return "failed"
        return "ok"
    except httpx.HTTPError:
        return "failed"
    finally:
        if owns_client:
            await http_client.aclose()


async def build_health_payload(
    settings: Settings,
    *,
    client: httpx.AsyncClient | None = None,
) -> dict[str, object]:
    model_credentials = derive_model_credentials(settings.openai_api_key)
    if model_credentials != "ok":
        model_reachable: ReachabilityStatus = "skipped"
    else:
        model_reachable = await probe_model_reachable(
            api_key=settings.openai_api_key or "",
            model=settings.openai_model,
            client=client,
        )

    status = derive_overall_status(
        model_credentials=model_credentials,
        model_reachable=model_reachable,
    )
    return {
        "status": status,
        "version": settings.api_version,
        "checks": {
            "process": "ok",
            "model_credentials": model_credentials,
            "model_reachable": model_reachable,
        },
    }


def create_health_router(settings: Settings | None = None) -> APIRouter:
    router = APIRouter(prefix="/v1", tags=["system"])
    resolved_settings = settings or get_settings()

    @router.get("/health")
    async def get_health() -> dict[str, object]:
        return await build_health_payload(resolved_settings)

    return router

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
    base_url: str,
    client: httpx.AsyncClient | None = None,
) -> ReachabilityStatus:
    """Perform a lightweight models request against the configured API base URL."""
    owns_client = client is None
    http_client = client or httpx.AsyncClient(timeout=5.0)
    models_url = f"{base_url.rstrip('/')}/v1/models"
    try:
        response = await http_client.get(
            models_url,
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
            base_url=settings.openai_base_url,
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

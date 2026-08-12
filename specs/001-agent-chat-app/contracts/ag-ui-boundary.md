# AG-UI Chat Boundary (v1)

**Contract version**: AG-UI protocol (pin: `@ag-ui/client` / `ag-ui-protocol` as
resolved at implementation lock)  
**Feature API version**: 1.0.0  
**Date**: 2026-08-12

## Scope

This document defines the **chat** producer/consumer boundary between:

- **Consumer**: `apps/web` — assistant-ui via `@assistant-ui/react-ag-ui`
- **Producer**: `apps/api` — Agno AgentOS `AGUI` interface

Health/readiness uses a **separate** project contract:
[health.openapi.yaml](./health.openapi.yaml).

## Endpoints (Agno AGUI interface)

Mounted at AgentOS root unless `AGUI(prefix=...)` is set (v1: **no prefix**).

| Method | Path | Content-Type | Description |
|--------|------|--------------|-------------|
| `POST` | `/agui` | `application/json` → `text/event-stream` | Run agent; stream AG-UI events |
| `GET` | `/status` | `application/json` | AG-UI interface liveness (auxiliary) |

## Request: `POST /agui`

Body: **AG-UI `RunAgentInput`** (JSON). Minimum fields used in v1:

```json
{
  "messages": [
    { "role": "user", "content": "你好" },
    { "role": "assistant", "content": "..." }
  ]
}
```

**Rules (v1)**:

- `messages` MUST contain the **full ordered thread** including the latest user
  turn (spec FR-004a).
- Roles: `user`, `assistant` (text content only).
- No attachments, tools, or metadata extensions in v1.

## Response: SSE stream

`Content-Type: text/event-stream`

Events follow AG-UI protocol encoding (`event:` + `data:` JSON lines). Key
event types for v1 acceptance:

| Event | Data (summary) | UI effect |
|-------|----------------|-----------|
| `TEXT_MESSAGE_CONTENT` | text delta | Append to assistant bubble |
| `RUN_FINISHED` | run complete | End streaming indicator |
| `RUN_ERROR` | error payload | Show 繁中 error; stop stream |

Canonical schemas: https://github.com/ag-ui-protocol/ag-ui

## Frontend connection

```text
VITE_API_BASE_URL=http://localhost:7777
assistant-ui runtime URL → ${VITE_API_BASE_URL}/agui
```

If `VITE_API_BASE_URL` unset/empty → web app blocks chat (spec FR-006).

## Backend configuration (v1 guardrails)

Agno Agent MUST NOT configure: `db`, tools, knowledge, memory. AgentOS MUST NOT
enable: `scheduler`, `mcp_server`, `authorization` (local dev only).

If `OPENAI_API_KEY` is missing or invalid, `POST /agui` MUST respond with **503**
and JSON `ErrorResponse` (`code`, `message`) **before** any SSE stream starts —
no fake or stubbed reply content (FR-011).

## Versioning policy

- **Breaking** AG-UI protocol changes → bump pinned protocol ref + migration note.
- **Additive** OpenAI/Agno upgrades → patch contract doc if event shapes change.
- Project `/v1/health` version independent (see health.openapi.yaml).

## Compatibility matrix

| Component | Version (plan lock) |
|-----------|---------------------|
| Agno | `agno[os,agui]` ≥ 2.5.x |
| assistant-ui | `@assistant-ui/react`, `@assistant-ui/react-ag-ui` latest stable at impl |
| OpenAI model | `gpt-4o-mini` default via `OPENAI_MODEL` |

# Data Model: Agent Chat App (001)

**Date**: 2026-08-12 (rev. 2 — Agno + assistant-ui + AG-UI)  
**Storage**: None server-side (no Agno `db` in v1)

## Overview

Message state lives in **assistant-ui runtime** (browser). Each send posts AG-UI
`RunAgentInput` to `POST /agui`; Agno Agent streams AG-UI events back. Backend
does not persist sessions.

## Entities

### Thread (assistant-ui runtime, client-only)

| Field | Type | Rules |
|-------|------|-------|
| `messages` | `ThreadMessage[]` | Single thread; managed by `@assistant-ui/react` runtime |
| `isRunning` | `boolean` | True while AG-UI stream active; blocks double-send |

**Lifecycle**: Empty on load; lost on full page refresh (v1).

### ThreadMessage (assistant-ui / AG-UI aligned)

Maps to AG-UI message parts in `RunAgentInput.messages`:

| Field | Type | Rules |
|-------|------|-------|
| `role` | `user` \| `assistant` | Required |
| `content` | `string` (text) | UTF-8; 繁中; max 4000 chars per message |
| `id` | `string` | Client/runtime-generated |

**Client validation**: non-empty trimmed content before send.

**Backend validation** (Agno/AG-UI layer): reject empty runs; enforce model token
limits via OpenAI (errors surfaced as AG-UI error events → 繁中 in UI adapter).

### AG-UI Stream Events (wire, transient)

Standard event types from [AG-UI protocol](https://github.com/ag-ui-protocol/ag-ui)
(referenced in `contracts/ag-ui-boundary.md`):

| Event | Purpose |
|-------|---------|
| `TEXT_MESSAGE_CONTENT` | Incremental assistant text (streaming) |
| `RUN_STARTED` / `RUN_FINISHED` | Stream lifecycle |
| `RUN_ERROR` | Failure with message |

assistant-ui `@assistant-ui/react-ag-ui` converts these to UI message updates.

### HealthStatus (`GET /v1/health` response)

See `contracts/health.openapi.yaml`:

| Field | Values |
|-------|--------|
| `status` | `healthy`, `degraded` |
| `version` | `1.0.0` |
| `checks.process` | `ok` |
| `checks.model_credentials` | `ok`, `missing`, `invalid` |
| `checks.model_reachable` | `ok`, `failed`, `skipped` |

### Agno Agent (server config entity, not persisted)

| Setting | v1 value |
|---------|----------|
| `name` | `chat` |
| `model` | `OpenAIChat` via `OPENAI_MODEL` |
| `db` | **unset** |
| `tools` | **none** |
| `memory` / `knowledge` | **disabled** |

## State Transitions (UI)

```text
Composer submit
  → append user message (complete)
  → runtime isRunning=true
  → AG-UI stream events append assistant content
  → RUN_FINISHED → isRunning=false
  → RUN_ERROR → show 繁中 error, isRunning=false
```

## Boundary Ownership

| Boundary | Schema source |
|----------|---------------|
| Web → API chat | AG-UI `RunAgentInput` @ `POST /agui` |
| API → OpenAI | Agno model driver (external) |
| API → Web stream | AG-UI SSE events |
| Web/ops → API health | OpenAPI `health.openapi.yaml` @ `GET /v1/health` |

## Why not Agno session DB?

Spec FR-010 and clarification **A** require no database and client-sent full
history. Agno `db` would persist sessions server-side — out of scope for v1.
Revisit only if product adds cross-device thread resume.

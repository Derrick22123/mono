# Data Model: Agent Chat App (001)

**Date**: 2026-08-12  
**Storage**: None (in-memory, client session only — no database in v1)

## Overview

All persistent entities live in the **browser session** (React state). The backend
translates each request's message list to an OpenAI chat completion call and
streams tokens back. No server-side thread store.

## Entities

### Thread (client-only)

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `messages` | `Message[]` | yes | Ordered ascending by send time; single thread per tab session |
| `streamingMessageId` | `string \| null` | yes | At most one agent message in `streaming` status |
| `inputDisabled` | `boolean` | derived | `true` when config error, streaming, or backend unreachable |

**Lifecycle**: Created empty on page load. Grows with each user send + agent
reply. Discarded on full page refresh (no restore in v1).

### Message (client + wire)

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `id` | `string` (UUID) | yes | Client-generated for UI keys |
| `role` | `"user" \| "assistant"` | yes | Maps to wire `ChatMessage.role` |
| `content` | `string` | yes | Plain text; UTF-8 Traditional Chinese supported |
| `status` | enum | client only | See state machine below |
| `errorMessage` | `string \| null` | client only | Traditional Chinese; set when `status=error` |

**Validation (client before send)**:

- User message: trimmed length ≥ 1, ≤ **4000** characters (v1 cap; prevents abuse)
- Whitespace-only: reject (FR edge case)

**Validation (backend on receive)**:

- `messages` array: length ≥ 1, ≤ **100** turns (50 user + 50 assistant max)
- Each message: `role` ∈ {user, assistant}, `content` non-empty string, ≤ 4000 chars
- Last message MUST be `role=user` (the new turn)
- Alternation not enforced (OpenAI accepts consecutive same-role); UI always appends user then assistant

### Message.status (client state machine)

```text
[user sends]
  → create user Message (status=complete)
  → create assistant Message (status=streaming)
  → on SSE delta: append content
  → on SSE done: status=complete
  → on SSE error / network fail: status=error, errorMessage set
```

**Invariant**: Only one message may be `streaming` at a time (FR double-submit guard).

### HealthStatus (backend response, ephemeral)

| Field | Type | Values |
|-------|------|--------|
| `status` | string | `healthy`, `degraded` |
| `version` | string | API contract version e.g. `1.0.0` |
| `checks.process` | string | `ok` |
| `checks.model_credentials` | string | `ok`, `missing`, `invalid` |
| `checks.model_reachable` | string | `ok`, `failed`, `skipped` |

**Rules**:

- `status=healthy` iff `model_credentials=ok` AND `model_reachable=ok`
- `status=degraded` otherwise (including missing key)

### StreamEvent (SSE wire, not persisted)

See `contracts/openapi.yaml` components. Types: `delta`, `done`, `error`.

## Relationships

```text
Thread 1──* Message
HealthStatus (standalone, per request)
StreamEvent* (transient, per chat request)
```

## Boundary ownership (Constitution IV)

| Boundary | Owner translates | Schema |
|----------|------------------|--------|
| Browser → Backend | Frontend serializes `ChatStreamRequest` | `contracts/openapi.yaml` |
| Backend → OpenAI | `backend/src/adapters/openai_adapter.py` | OpenAI API (external) |
| Backend → Browser | Backend frames SSE events | `contracts/openapi.yaml` |

No shared TypeScript/Python type package in v1; OpenAPI is the contract source
of truth. Frontend types generated or hand-maintained to match spec version.

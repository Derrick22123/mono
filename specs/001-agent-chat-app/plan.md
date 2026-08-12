# Implementation Plan: Agent Chat App

**Branch**: `001-agent-chat-app` | **Date**: 2026-08-12 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-agent-chat-app/spec.md`

## Summary

Deliver a minimal Traditional Chinese agent chat web app: one in-browser thread,
streaming replies from a real OpenAI model, stateless backend, versioned HTTP
contract (`/v1/health`, `/v1/chat/stream` SSE), and `VITE_API_BASE_URL` for
frontend backend configuration.

**Architecture**: FastAPI backend (Python 3.12) + Vite/React/TypeScript SPA.
Single deployable serves API + built static assets (`make serve`). Local dev may
run Vite + Uvicorn as two processes for hot reload (justified in Complexity
Tracking). Client holds thread state and sends full history each turn.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend)

**Primary Dependencies**: FastAPI, Uvicorn, openai SDK, httpx (backend);
Vite, React 19 (frontend)

**Storage**: N/A (no database; client session state only)

**Testing**: pytest + httpx AsyncClient (backend); vitest optional (frontend v1);
contract source: `contracts/openapi.yaml`

**Target Platform**: Linux/macOS local dev; modern browsers (Chrome/Firefox/Safari
current −1)

**Project Type**: web application (SPA + HTTP API)

**Performance Goals**: First SSE `delta` within 3s p95 on warm backend with valid
API key; UI remains responsive during streams up to 4000-char messages

**Constraints**: Real OpenAI API required; no stub fallback; Traditional Chinese
UI copy; no auth/RAG/tools/uploads/production deploy in v1

**Scale/Scope**: Single user/session per tab; ≤100 messages per request; local/dev
trust boundary

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Phase 0 | Post-Phase 1 | Notes |
|-----------|-------------|--------------|-------|
| I — No distribute by default | ⚠️ Dev dual-process | ✅ Pass with waiver | Production/CI: one Uvicorn serves API+static. Dev: Vite+Uvicorn documented in Complexity Tracking |
| II — Deletion over extension | ✅ Pass | ✅ Pass | Flat modules: `api/`, `adapters/`, `domain/`; no plugin framework |
| III — Explicit dependencies | ✅ Pass | ✅ Pass | FastAPI `Depends()` injects settings + OpenAI client |
| IV — Contract at boundary | ✅ Pass | ✅ Pass | `contracts/openapi.yaml` v1.0.0; adapter owns OpenAI mapping |
| V — Test transformation | ✅ Pass | ✅ Pass | Unit: validation/SSE framing; integration: HTTP with mocked OpenAI |
| VI — Structured events | ✅ Pass | ✅ Pass | JSON logs with `request_id`, `event` per chat/health |
| VII — Recovery | ✅ Pass | ✅ Pass | No DB; rollback = redeploy prior build |
| VIII — Attention finite | ✅ N/A v1 | ✅ N/A v1 | No paging/alerting in v1 local scope |
| IX — Value at user | ✅ Pass | ✅ Pass | quickstart.md defines shipped validation |
| X — Commands discoverable | ✅ Pass | ✅ Pass | Root Makefile; CI uses same targets |

**Gate result**: PASS (dev dual-process waiver recorded below).

## Project Structure

### Documentation (this feature)

```text
specs/001-agent-chat-app/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── openapi.yaml     # Phase 1 — versioned HTTP contract
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 (/speckit-tasks — not yet created)
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml
├── src/
│   └── app/
│       ├── main.py              # FastAPI app factory, static mount
│       ├── config.py            # Settings from env (explicit)
│       ├── api/
│       │   ├── health.py        # GET /v1/health
│       │   └── chat.py          # POST /v1/chat/stream (SSE)
│       ├── adapters/
│       │   └── openai_adapter.py  # OpenAI stream → SSE events
│       ├── domain/
│       │   ├── messages.py      # Validation (pure)
│       │   └── sse.py           # SSE framing (pure)
│       └── logging.py           # Structured JSON logger
└── tests/
    ├── unit/
    └── integration/

frontend/
├── package.json
├── vite.config.ts
├── index.html
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── components/
    │   ├── ChatThread.tsx
    │   ├── MessageInput.tsx
    │   └── ConfigError.tsx
    ├── hooks/
    │   └── useChatStream.ts
    ├── lib/
    │   ├── api.ts               # fetch + SSE consumer
    │   └── config.ts            # VITE_API_BASE_URL guard
    └── i18n/
        └── zh-TW.ts             # Traditional Chinese UI strings

Makefile                         # Command index (install, dev, test, …)
```

**Structure Decision**: Web app layout (`backend/` + `frontend/`) with **single
runtime** for ship (`make serve` mounts `frontend/dist` on FastAPI). Matches
spec's browser+backend shape while keeping production as one deployable per
Constitution I.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Two processes in `make dev` (Vite + Uvicorn) | Frontend HMR requires Vite dev server; bundling on every save would slow iteration | Single Python-only UI (HTMX) sacrifices streaming UX and TS tooling agreed in research R5 |
| Separate `backend/` and `frontend/` directories | Clear boundary ownership for OpenAPI contract vs UI; still one deployable via static mount | Monolithic Jinja templates don't match streaming SPA requirement in spec |

## Phase 0 & Phase 1 Outputs

| Artifact | Path | Status |
|----------|------|--------|
| Research | [research.md](./research.md) | ✅ Complete |
| Data model | [data-model.md](./data-model.md) | ✅ Complete |
| Contracts | [contracts/openapi.yaml](./contracts/openapi.yaml) | ✅ Complete |
| Quickstart | [quickstart.md](./quickstart.md) | ✅ Complete |

## Next Step

Run `/speckit-tasks` to decompose implementation from this plan and contracts.

# Research: Agent Chat App (001)

**Date**: 2026-08-12  
**Feature**: `specs/001-agent-chat-app/spec.md`

## R1 — Runtime topology (single deployable vs split)

**Decision**: One **backend deployable** (FastAPI) owns the HTTP API, model adapter,
and (when built) serves the compiled SPA as static assets. Local development MAY
run Vite dev server + Uvicorn as **two processes** for hot reload only; production
and CI validation use the single backend process serving `frontend/dist/`.

**Rationale**: Aligns with Constitution **I** (no distribution by default). The
browser↔backend boundary is required by the product; splitting into separate
*deployables* would add coordination without v1 benefit. Dev dual-process is a
DX convenience, not a service boundary.

**Alternatives considered**:

| Alternative | Rejected because |
|-------------|------------------|
| Separate frontend container/service in v1 | Violates single-deployable default; no scale/org justification |
| HTMX-only server-rendered UI in one Python file | Valid for single process but weaker streaming UX tooling for incremental DOM updates |
| Next.js full-stack | Heavier framework; blurs frontend/backend ownership for a minimal chat |

## R2 — Backend language & framework

**Decision**: **Python 3.12 + FastAPI + Uvicorn**, managed with **uv** (already
used in repo tooling).

**Rationale**: Native async, first-class SSE/streaming support, small module
surface, fits Constitution **II** (deletable modules). Team already uses `uv`.

**Alternatives considered**: Node/Express (viable SSE but duplicates Python
tooling); Go (more boilerplate for v1 scope).

## R3 — External model provider

**Decision**: **OpenAI Chat Completions API** (streaming) via official
`openai` Python SDK. Credentials: `OPENAI_API_KEY` (required). Optional:
`OPENAI_MODEL` (default `gpt-4o-mini`), `OPENAI_BASE_URL` (for compatible
gateways).

**Rationale**: Spec clarification **B** requires a real external model with env
credentials. OpenAI streaming is stable, well-documented, and supports
Traditional Chinese. Health check validates key presence and performs a minimal
API reachability probe (models list or lightweight call).

**Alternatives considered**: Anthropic (valid; deferred to keep one adapter in
v1); local Ollama (still "external" but ops burden; out of v1 quickstart scope).

## R4 — Streaming protocol (browser ↔ backend)

**Decision**: **Server-Sent Events (SSE)** on `POST /v1/chat/stream` with
`Content-Type: text/event-stream`. Request body carries full thread history as
JSON (Constitution **IV** contract in `contracts/openapi.yaml`).

**Rationale**: SSE is unidirectional (server→client), works over HTTP/1.1,
simple to consume with `EventSource` or `fetch` + readable stream. Matches FR-003
progressive reply without WebSocket complexity.

**Alternatives considered**: WebSocket (bidirectional overkill for request→stream
pattern); chunked JSON lines (less standard error semantics).

## R5 — Frontend stack

**Decision**: **Vite + React 19 + TypeScript**. Config: `VITE_API_BASE_URL`
(required at build/dev time; empty → UI blocks chat per clarification **B**).

**Rationale**: Fast local dev, explicit env injection, small component model for
one chat page. Thread state lives in React state (no persistence).

**Alternatives considered**: Vue/Svelte (fine; React chosen for ecosystem);
vanilla TS (less structure for streaming state machine).

## R6 — Conversation state

**Decision**: **Client-owned thread**; each `POST /v1/chat/stream` includes
complete ordered `messages[]`. Backend is **stateless** (no session store, no DB).

**Rationale**: Spec clarification **A**; satisfies FR-004a and FR-010 (no database).

## R7 — Health semantics

**Decision**: `GET /v1/health` returns JSON with top-level `status`:
`healthy` | `degraded`. `degraded` when `OPENAI_API_KEY` missing/empty or
provider probe fails. HTTP **200** for both (body carries semantics); UI treats
`degraded` as not ready.

**Rationale**: Clarification **B** — process up but creds bad ≠ healthy. HTTP 200
allows load balancers to distinguish process death (connection error) vs logical
unready (parse body).

**Alternatives considered**: HTTP 503 on degraded (rejected: conflates crash with
config issue for simple local ops).

## R8 — Observability

**Decision**: Structured JSON logs per request (`request_id`, `event`, `duration_ms`,
`model`, `error_code`). No metrics stack in v1; logs are the primitive (Constitution **VI**).

## R9 — Command surface (Constitution **X**)

**Decision**: Root **`Makefile`** as command index:

| Command | Action |
|---------|--------|
| `make install` | Install backend + frontend deps via uv/npm |
| `make dev` | Run backend + Vite dev (two terminals or concurrent) |
| `make build` | Build frontend → `frontend/dist`, verify backend imports |
| `make test` | Backend unit + integration (same as CI) |
| `make lint` | Ruff + eslint |
| `make serve` | Single-process: backend serves API + static dist |
| `make health` | Curl `/v1/health` |

CI invokes `make test`, `make lint`, `make build` only.

## R10 — Testing strategy (Constitution **V**)

**Decision**:

- **Unit**: message validation, SSE event framing, health status derivation
  (pure functions in `backend/src/`).
- **Integration**: HTTP tests against FastAPI app with **mocked OpenAI client**
  (mock what you don't own at boundary tests—OpenAI is external; use dependency
  override). One integration test with real API marked `@pytest.mark.live` optional.
- **Contract**: Schemathesis or openapi spec diff in CI (optional v1); manual
  contract files in `contracts/` are source of truth.

All NEEDS CLARIFICATION from Technical Context: **resolved** by decisions above.

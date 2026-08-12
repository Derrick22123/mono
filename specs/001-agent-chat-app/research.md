# Research: Agent Chat App (001)

**Date**: 2026-08-12 (revised after architecture review)  
**Feature**: `specs/001-agent-chat-app/spec.md`

## Architecture Re-Analysis (2026-08-12)

User proposed:

```text
apps/
├── web/    # assistant-ui frontend
└── api/    # Agno AgentOS backend
```

Previous plan used hand-rolled FastAPI SSE + custom React chat components. After
comparing against spec, constitution, and the proposed stack:

| Criterion | Custom FastAPI + React | **Agno AgentOS + assistant-ui** |
|-----------|------------------------|----------------------------------|
| Streaming chat UX | Build state machine, auto-scroll, a11y | **assistant-ui primitives (production-grade)** |
| Agent + model wiring | Custom OpenAI adapter | **Agno Agent (maintained SDK)** |
| Boundary contract | Custom SSE schema (greenfield) | **AG-UI protocol (versioned, ecosystem)** |
| Spec: no DB v1 | Natural fit | **Fit if `db=` omitted on Agent** |
| Spec: full history from UI | Manual in fetch body | **AG-UI `RunAgentInput` + assistant-ui runtime** |
| Spec: real external model | Direct OpenAI SDK | **Agno OpenAI model driver** |
| Constitution II (deletion) | Smaller deps, more custom code | **Less custom code; framework surface area** |
| Constitution IV (contracts) | Single OpenAPI file | **AG-UI protocol + thin `/v1/health` OpenAPI** |
| v1 out-of-scope (tools/RAG) | Easy to omit | **Must explicitly disable Agno features** |

**Conclusion**: The proposed stack is **better aligned** with the product (agent
chat with streaming) and reduces bespoke streaming/UI code. Adopt it with
explicit guardrails: no database, no tools/memory/knowledge, AG-UI boundary only,
plus a thin project-owned `/v1/health` for spec-accurate credential semantics.

---

## R1 — Monorepo layout & runtime topology

**Decision**: **`apps/api`** (Agno AgentOS) + **`apps/web`** (assistant-ui SPA).
Production/CI single deployable: AgentOS serves built static assets from
`apps/web/dist` (same pattern as before, different paths). Local dev runs
Uvicorn + Vite (dual-process waiver unchanged).

**Rationale**: `apps/` is conventional for full-stack monorepos; separates
contract owner (api) from UI owner (web) while keeping one ship artifact.

**Alternatives considered**: Flat `backend/`/`frontend/` (rejected: user
requested `apps/`); Agno `agent-ui` Next template (rejected: user specified
assistant-ui, not Agno's reference UI).

## R2 — Backend: Agno AgentOS

**Decision**: **Agno AgentOS** with one `Agent`, **`AGUI` interface**, **no `db`**
on Agent or AgentOS in v1. Package: `agno[os,agui]`, managed with **uv**.

Minimal bootstrap:

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI

chat_agent = Agent(
    name="chat",
    model=OpenAIChat(id=os.getenv("OPENAI_MODEL", "gpt-4o-mini")),
    instructions="以繁體中文回覆。",
    # v1: NO db, tools, memory, knowledge
)

agent_os = AgentOS(
    agents=[chat_agent],
    interfaces=[AGUI(agent=chat_agent)],
    tracing=False,  # optional off for minimal v1
)
app = agent_os.get_app()
# + mount /v1/health router (project-owned)
```

Default port **7777** (`AGENT_OS_PORT`). Credentials: `OPENAI_API_KEY` (required).

**Rationale**: AgentOS is FastAPI under the hood (Constitution I compatible).
AG-UI exposes `POST /agui` (stream) and `GET /status`. Omitting `db` keeps v1
stateless per spec clarification **A** and FR-010.

**Alternatives considered**: Raw FastAPI + OpenAI SDK (previous plan — more
custom code); Agno REST `/agents/{id}/runs` with form sessions (conflicts with
client-owned history unless history passed each time — AG-UI is cleaner for UI).

## R3 — Frontend: assistant-ui

**Decision**: **Vite + React 19 + TypeScript + assistant-ui** in `apps/web`.
Runtime: **`@assistant-ui/react-ag-ui`** connected to `{API_BASE}/agui`.
Scaffold UI via assistant-ui CLI (Thread, Composer primitives).

Config: **`VITE_API_BASE_URL`** (required) → base URL of AgentOS e.g.
`http://localhost:7777`. Empty → block chat with 繁中 error (spec clarification).

**Rationale**: assistant-ui handles streaming display, auto-scroll, composer
state, and accessibility — directly addresses SC-002 without custom hooks.
Official AG-UI adapter matches Agno's `AGUI` interface.

**Alternatives considered**: Hand-rolled React chat (previous R5 — rejected on
re-analysis); Agno `agent-ui` Next.js template (different stack from user ask).

## R4 — Boundary protocol (Constitution IV)

**Decision**: Primary chat boundary = **AG-UI protocol** (pinned ref in
`contracts/ag-ui-boundary.md`). Supplementary **OpenAPI 3.1** for project-owned
**`GET /v1/health`** in `contracts/health.openapi.yaml` (credential readiness
semantics from spec clarification **B**).

| Endpoint | Owner | Purpose |
|----------|-------|---------|
| `POST /agui` | Agno `AGUI` | Stream chat (AG-UI events) |
| `GET /status` | Agno `AGUI` | Interface liveness (informational) |
| `GET /v1/health` | `apps/api` thin router | Spec acceptance: healthy/degraded + credential checks |

**Rationale**: AG-UI is the industry-facing agent↔UI contract; `/v1/health`
preserves spec testability without reimplementing chat streaming.

## R5 — Conversation state

**Decision**: **Unchanged from clarification A** — assistant-ui + AG-UI runtime
sends full message history in `RunAgentInput`. No Agno session DB; do not pass
persistent `session_id` for v1 (ephemeral per tab).

## R6 — Health semantics

**Decision**: **`GET /v1/health`** returns `{ status: healthy|degraded, checks }`.
`degraded` when `OPENAI_API_KEY` missing/invalid (probe OpenAI models list or
Agno model init). Agno `GET /status` documented as auxiliary, not acceptance
substitute.

## R7 — Observability

**Decision**: Structured JSON logs in thin health/chat middleware wrapper
(`request_id`, `event`). Agno tracing **disabled** in v1 to avoid implicit DB;
enable in v2 if needed.

## R8 — Command surface (Constitution X)

**Decision**: Root **`Makefile`** targeting `apps/`:

| Command | Action |
|---------|--------|
| `make install` | `uv sync` in `apps/api`; `pnpm install` in `apps/web` |
| `make dev` | AgentOS + Vite dev (concurrently) |
| `make build` | `pnpm build` → `apps/web/dist`; verify api imports |
| `make test` | pytest in `apps/api` |
| `make lint` | ruff + eslint |
| `make serve` | AgentOS serves API + `apps/web/dist` |
| `make health` | `curl /v1/health` |

## R9 — Testing strategy

**Decision**:

- **Unit** (`apps/api`): health derivation, env validation helpers
- **Integration**: FastAPI TestClient for `/v1/health`; AG-UI `/agui` with mocked
  model stream (patch Agno model or use test double)
- **E2E manual**: quickstart scenarios via browser
- **Do not mock** owned `/v1/health` logic; **do mock** OpenAI/Agno model at boundary

## R10 — v1 Agno feature guardrails (out-of-scope enforcement)

**Decision**: Explicitly **disabled** in v1 Agent definition:

- `db` / SqliteDb / Postgres
- `tools`, `knowledge`, `enable_agentic_memory`
- AgentOS: `scheduler`, `mcp_server`, `authorization` (local trust boundary)

Violations of FR-010 caught in code review + quickstart scope check (SC-005).

All NEEDS CLARIFICATION: **resolved**.

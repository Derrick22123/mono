# Quickstart: Agent Chat App (001)

**Purpose**: E2E validation for Agno AgentOS + assistant-ui stack.  
**Contracts**:
- Chat: [contracts/ag-ui-boundary.md](./contracts/ag-ui-boundary.md)
- Health: [contracts/health.openapi.yaml](./contracts/health.openapi.yaml)  
**Data model**: [data-model.md](./data-model.md)

## Prerequisites

- Python 3.12+, [uv](https://docs.astral.sh/uv/)
- Node.js 20+, **pnpm**
- `OPENAI_API_KEY` (required — real model per spec)

## Environment variables

| Variable | Where | Required | Example |
|----------|-------|----------|---------|
| `OPENAI_API_KEY` / `DEEPSEEK_API_KEY` | `apps/api` | yes | `sk-...` |
| `OPENAI_BASE_URL` | `apps/api` | no | `https://api.deepseek.com` |
| `OPENAI_MODEL` | `apps/api` | no | `deepseek-v4-flash` |
| `AGENT_OS_PORT` | `apps/api` | no | `7777` (default) |
| `VITE_API_BASE_URL` | `apps/web` | yes | `http://localhost:7777` |

## Setup (after implementation)

```bash
make install
export OPENAI_API_KEY=sk-...
export VITE_API_BASE_URL=http://localhost:7777
```

## Scenario 1 — Health check (spec AC #2)

**Given** API running with valid key:

```bash
make health
# curl -s http://localhost:7777/v1/health | jq
```

**Expected**: `"status": "healthy"`.

**Given** API running without `OPENAI_API_KEY`:

**Expected**: `"status": "degraded"`, `model_credentials: "missing"`.

## Scenario 2 — AG-UI stream (API-level)

With Agno cookbook pattern or curl against `/agui` per AG-UI docs — verify SSE
events arrive. (Detailed curl depends on AG-UI `RunAgentInput` envelope; prefer
UI scenario 3 for acceptance.)

## Scenario 3 — Full UI flow (spec P1)

> **MVP note**: Demo MVP (US1 only) requires `export VITE_API_BASE_URL=...` manually.
> ConfigError UI and empty-env blocking ship in US3 (tasks T037–T040).

1. `make dev`
2. Open Vite URL (e.g. `http://localhost:5173`)
3. Verify UI copy is **繁體中文**
4. Send: `請用三句話介紹你自己`
5. Observe streaming partial text before completion (SC-002)
6. Follow-up: `剛才第一句是什麼？` — agent MUST reference first reply sentence (FR-004a / AG-UI full `messages[]`). Verify via integration test `tests/integration/test_agui_history.py` or browser multi-turn.
7. Confirm prior assistant message remains visible after stream completes; refresh clears thread (v1 session-only).

## Scenario 4 — Missing `VITE_API_BASE_URL`

Unset variable, restart web dev server.

**Expected**: 繁中 configuration error; chat blocked.

## Scenario 5 — Backend URL config (spec AC #3)

Change `VITE_API_BASE_URL` to alternate port; restart web; chat succeeds.

## Scenario 6 — Single-process serve (Constitution I)

```bash
make build && make serve
# http://localhost:7777 — SPA + /agui + /v1/health same origin
```

## Out-of-scope verification (SC-005)

Confirm v1 Agent has no `db`, tools, RAG, login, or upload UI.

Additional checks (task T045):

- No new `*.db` or session persistence files appear in the repo after a full chat session
- `apps/api/src/app/agent.py` has no `db=` / `SqliteDb` / tools configuration

## Optional: Agno AG-UI `/status`

```bash
curl -s http://localhost:7777/status
```

Informational only; **acceptance health** is `/v1/health`.

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
| `OPENAI_API_KEY` | `apps/api` | yes | `sk-...` |
| `OPENAI_MODEL` | `apps/api` | no | `gpt-4o-mini` |
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

1. `make dev`
2. Open Vite URL (e.g. `http://localhost:5173`)
3. Verify UI copy is **繁體中文**
4. Send: `請用三句話介紹你自己`
5. Observe streaming partial text (SC-002)
6. Follow-up: `剛才第一句是什麼？` — confirms full history via AG-UI

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

## Optional: Agno AG-UI `/status`

```bash
curl -s http://localhost:7777/status
```

Informational only; **acceptance health** is `/v1/health`.

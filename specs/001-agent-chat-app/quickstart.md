# Quickstart: Agent Chat App (001)

**Purpose**: End-to-end validation scenarios for v1 (local/dev).  
**Contracts**: [contracts/openapi.yaml](./contracts/openapi.yaml)  
**Data model**: [data-model.md](./data-model.md)

## Prerequisites

- Python 3.12+, [uv](https://docs.astral.sh/uv/)
- Node.js 20+ (for frontend build/dev)
- `OPENAI_API_KEY` set in environment (real model required per spec)
- Optional: `OPENAI_MODEL` (default `gpt-4o-mini`)

## Environment variables

| Variable | Where | Required | Purpose |
|----------|-------|----------|---------|
| `OPENAI_API_KEY` | backend | yes | OpenAI credentials |
| `OPENAI_MODEL` | backend | no | Model id override |
| `VITE_API_BASE_URL` | frontend build/dev | yes | Backend base URL e.g. `http://localhost:8000` |

## Setup (after implementation)

```bash
make install
export OPENAI_API_KEY=sk-...
export VITE_API_BASE_URL=http://localhost:8000
```

## Scenario 1 — Health check (P2)

**Given** backend running with valid `OPENAI_API_KEY`

```bash
make health
# or: curl -s http://localhost:8000/v1/health | jq
```

**Expected**: `"status": "healthy"`, `checks.model_credentials: "ok"`.

**Given** backend running without `OPENAI_API_KEY`

**Expected**: `"status": "degraded"`, `checks.model_credentials: "missing"`.

## Scenario 2 — Stream chat via API (P1 core)

```bash
curl -N -X POST http://localhost:8000/v1/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"用繁體中文說你好"}]}'
```

**Expected**: SSE `event: delta` lines with growing text, ending with `event: done`.

## Scenario 3 — Full UI flow (P1 acceptance)

1. Terminal A: `make dev` (or backend + frontend separately)
2. Open browser to Vite URL (typically `http://localhost:5173`)
3. Confirm UI labels/errors are **Traditional Chinese**
4. Send: `請用三句話介紹你自己`
5. Observe partial reply text before stream completes
6. Send follow-up: `剛才第一句是什麼？`
7. Confirm second reply references prior context (full history sent)

**Pass criteria**: SC-001, SC-002 from spec.md.

## Scenario 4 — Missing frontend config (clarification B)

1. Unset `VITE_API_BASE_URL`, rebuild/restart frontend
2. Open chat page

**Expected**: Configuration error in Traditional Chinese; send disabled.

## Scenario 5 — Configurable backend URL (AC #3)

1. Run backend on port 8000
2. Set `VITE_API_BASE_URL=http://localhost:8000`, start UI → chat works
3. Stop backend, start on port 8001, set `VITE_API_BASE_URL=http://localhost:8001`,
   restart UI → chat works against new port

**Pass criteria**: SC-004.

## Scenario 6 — Error paths

| Action | Expected UI (繁中) |
|--------|-------------------|
| Submit empty message | Blocked / prompt to enter text |
| Backend stopped mid-stream | Streaming stops; error shown; prior messages remain |
| Double-click send while streaming | Second send blocked |
| Missing API key, attempt chat | Error message; no fake reply |

## Single-process validation (Constitution I)

```bash
make build
make serve
# Open http://localhost:8000 — SPA + API same origin
```

**Expected**: Chat and `/v1/health` work without Vite dev server.

## Rollback note (Constitution VII)

v1 has no database migrations. Rollback = redeploy previous build artifact or
`git checkout` + `make serve`. Documented in implementation PR.

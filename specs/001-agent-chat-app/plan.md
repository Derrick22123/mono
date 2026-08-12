# Implementation Plan: Agent Chat App

**Branch**: `001-agent-chat-app` | **Date**: 2026-08-12 (rev. 2) | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-agent-chat-app/spec.md`  
**User architecture directive**: `apps/web` (assistant-ui) + `apps/api` (Agno AgentOS)

## Summary

Traditional Chinese agent chat: one in-browser thread, streaming replies via
**AG-UI protocol** between **assistant-ui** (`apps/web`) and **Agno AgentOS**
(`apps/api`). Real OpenAI model (env credentials). Client-owned thread history;
backend stateless (no DB). Versioned boundaries: AG-UI for chat +
OpenAPI `/v1/health` for readiness checks. `VITE_API_BASE_URL` configures frontend
→ API base URL.

## Technical Context

**Language/Version**: Python 3.12 (api), TypeScript 5.x (web)

**Primary Dependencies**:
- API: `agno[os,agui]`, OpenAI via Agno model driver, uvicorn
- Web: `@assistant-ui/react`, `@assistant-ui/react-ag-ui`, Vite, React 19

**Storage**: N/A (Agent and AgentOS run **without `db`** in v1)

**Testing**: pytest + httpx (api); manual/E2E via quickstart (web v1)

**Target Platform**: Linux/macOS local dev; modern browsers

**Project Type**: Monorepo web application (`apps/api` + `apps/web`)

**Performance Goals**: First AG-UI content event within 3s p95; UI responsive
during long streams (assistant-ui handles virtualization optional later)

**Constraints**: Real OpenAI; 繁中 UI; no auth/DB/RAG/tools/uploads/prod deploy;
Agno optional features explicitly off

**Scale/Scope**: Single tab/session; local trust boundary

## Constitution Check

*GATE: Pre-Phase 0 and post-Phase 1*

| Principle | Status | Notes |
|-----------|--------|-------|
| I — No distribute by default | ✅ Pass (waiver) | One deployable via `make serve`; dev dual-process documented |
| II — Deletion over extension | ✅ Pass | Thin `health` router + minimal Agent config; no custom chat framework |
| III — Explicit dependencies | ✅ Pass | Settings via env; Agent/model injected in `main.py` only |
| IV — Contract at boundary | ✅ Pass | AG-UI protocol doc + `health.openapi.yaml` v1.0.0 |
| V — Test transformation | ✅ Pass | Unit on health logic; integration on HTTP boundaries |
| VI — Structured events | ✅ Pass | JSON request logs with `request_id` |
| VII — Recovery | ✅ Pass | No migrations; redeploy rollback |
| VIII — Attention finite | N/A v1 | |
| IX — Value at user | ✅ Pass | quickstart.md |
| X — Commands discoverable | ✅ Pass | Makefile |

**Gate result**: PASS

## Project Structure

### Documentation (this feature)

```text
specs/001-agent-chat-app/
├── plan.md
├── research.md              # includes architecture re-analysis
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── ag-ui-boundary.md    # AG-UI chat boundary (version pinned)
│   └── health.openapi.yaml  # GET /v1/health (project-owned)
└── checklists/
```

### Source Code (repository root)

```text
apps/
├── api/
│   ├── pyproject.toml           # agno[os,agui], uv project
│   ├── src/
│   │   └── app/
│   │       ├── main.py          # AgentOS + AGUI + static mount + health router
│   │       ├── agent.py         # Single Agent factory (no db/tools)
│   │       ├── config.py        # OPENAI_API_KEY, OPENAI_MODEL, paths
│   │       ├── health.py        # GET /v1/health (spec semantics)
│   │       └── logging.py       # Structured JSON logs
│   └── tests/
│       ├── unit/
│       └── integration/
└── web/
    ├── package.json
    ├── vite.config.ts
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx
    │   ├── components/
    │   │   └── assistant-ui/    # CLI-scaffolded Thread/Composer
    │   ├── lib/
    │   │   ├── runtime.ts         # useAgUiRuntime({ url: `${base}/agui` })
    │   │   └── config.ts          # VITE_API_BASE_URL guard
    │   └── i18n/
    │       └── zh-TW.ts           # 繁中 labels/errors
    └── dist/                      # built assets (served by api in prod)

Makefile
```

**Structure Decision**: User-requested **`apps/` monorepo**. Agno AgentOS owns
agent execution and AG-UI endpoint; assistant-ui owns chat UX. Single runtime:
AgentOS serves `apps/web/dist` + `/agui` + `/v1/health`.

## Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────┐
│  Browser                                                     │
│  apps/web — assistant-ui (Thread, Composer)                 │
│  State: messages[] in runtime (session-only)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │ AG-UI protocol (SSE)
                           │ POST {base}/agui
                           │ GET  {base}/v1/health  (readiness)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  apps/api — Agno AgentOS (FastAPI / Uvicorn)                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ AGUI router │  │ /v1/health   │  │ StaticFiles      │  │
│  │ POST /agui  │  │ (project)    │  │ apps/web/dist    │  │
│  └──────┬──────┘  └──────────────┘  └──────────────────┘  │
│         │                                                    │
│         ▼                                                    │
│  Agent (no db, no tools) ──► OpenAI API (streaming)         │
└─────────────────────────────────────────────────────────────┘
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Dev: Vite + Uvicorn | HMR for assistant-ui components | Rebuilding SPA each save is too slow |
| Two packages in `apps/` | Clear api vs web ownership | Single Python+inline HTML fails assistant-ui React requirement |
| AG-UI + `/v1/health` | AG-UI `/status` ≠ spec credential semantics | Custom-only SSE (prev plan) duplicates assistant-ui + Agno value |

## Phase 0 & Phase 1 Outputs

| Artifact | Path | Status |
|----------|------|--------|
| Research (incl. re-analysis) | [research.md](./research.md) | ✅ |
| Data model | [data-model.md](./data-model.md) | ✅ Updated |
| AG-UI boundary | [contracts/ag-ui-boundary.md](./contracts/ag-ui-boundary.md) | ✅ |
| Health contract | [contracts/health.openapi.yaml](./contracts/health.openapi.yaml) | ✅ |
| Quickstart | [quickstart.md](./quickstart.md) | ✅ Updated |

## Next Step

Run `/speckit-tasks` to implement `apps/api` and `apps/web` from this plan.

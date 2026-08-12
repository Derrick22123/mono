---
description: "Task list for Agent Chat App (001) — Agno AgentOS + assistant-ui"
---

# Tasks: Agent Chat App

**Input**: Design documents from `/specs/001-agent-chat-app/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Backend tests for `/v1/health` and `/agui` stream (plan R10 + Constitution V).

**Organization**: Tasks grouped by user story for independent implementation and validation.

**Remediation**: Applied 2026-08-12 from `/speckit-analyze` supplement (coverage gaps, edge cases, Constitution VI).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: US1, US2, US3 mapped to spec.md user stories

## Path Conventions

Monorepo layout from plan.md:

- **API**: `apps/api/src/app/`
- **Web**: `apps/web/src/`
- **Commands**: root `Makefile`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize `apps/api` + `apps/web` monorepo and command surface

- [x] T001 Create `apps/api/src/app/` and `apps/web/src/` directory tree per specs/001-agent-chat-app/plan.md
- [x] T002 Initialize `apps/api/pyproject.toml` with uv, Python 3.12, and `agno[os,agui]` dependencies
- [x] T003 [P] Initialize `apps/web/package.json` with Vite, React 19, TypeScript, `@assistant-ui/react`, `@assistant-ui/react-ag-ui`
- [x] T004 [P] Create root `Makefile` with `install`, `dev`, `build`, `test`, `lint`, `serve`, `health` targets per research.md R8
- [x] T005 [P] Configure Ruff lint/format in `apps/api/pyproject.toml`
- [x] T006 [P] Configure ESLint in `apps/web/eslint.config.js`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: AgentOS bootstrap, shared config/logging, web shell — **blocks all user stories**

**⚠️ CRITICAL**: No user story work until this phase completes

- [x] T007 Implement `apps/api/src/app/config.py` for `OPENAI_API_KEY`, `OPENAI_MODEL`, `AGENT_OS_PORT`, static dist path
- [x] T008 [P] Implement `apps/api/src/app/logging.py` structured JSON logger (`request_id`, `event`)
- [x] T009 Implement `apps/api/src/app/agent.py` Agent factory — no `db`, tools, memory, or knowledge (research R10 guardrails)
- [x] T010 Implement `apps/api/src/app/main.py` with AgentOS, `AGUI` interface, and CORS for Vite dev origin
- [x] T011 Add `apps/api/src/app/__init__.py` and uvicorn entry `apps/api/src/app/main.py:app`
- [x] T012 [P] Create `apps/web/index.html` and `apps/web/src/main.tsx` Vite React entry
- [x] T013 [P] Create `apps/web/vite.config.ts` with `envPrefix: 'VITE_'` and dev server proxy optional note
- [x] T014 Add request logging middleware in `apps/api/src/app/main.py` using `apps/api/src/app/logging.py` (Constitution VI — before chat traffic)
- [x] T015 [P] Add `apps/api/tests/conftest.py` with FastAPI app fixture and model override hook

**Checkpoint**: `uv run uvicorn` serves AgentOS with `POST /agui`; structured logs on each request

---

## Phase 3: User Story 1 — Send message and see streaming reply (Priority: P1) 🎯 MVP

**Goal**: User sends Traditional Chinese message; assistant reply streams incrementally in single thread

**Independent Test**: Open chat UI, send `請用三句話介紹你自己`, observe partial text before stream completes; follow-up `剛才第一句是什麼？` confirms context (FR-004a, SC-001, SC-002)

### Implementation for User Story 1

- [x] T016 [P] [US1] Scaffold assistant-ui `Thread` and `Composer` into `apps/web/src/components/assistant-ui/`
- [x] T017 [P] [US1] Implement `apps/web/src/lib/runtime.ts` using `@assistant-ui/react-ag-ui` with URL `${VITE_API_BASE_URL}/agui`; document that runtime sends full `messages[]` per FR-004a
- [x] T018 [US1] Implement `apps/web/src/App.tsx` with `AssistantRuntimeProvider` and single `Thread` (no ThreadList)
- [x] T019 [P] [US1] Create `apps/web/src/i18n/zh-TW.ts` with 繁中 labels, empty-state, and streaming indicator strings
- [x] T020 [US1] Apply 繁中 strings to `apps/web/src/components/assistant-ui/` and `apps/web/src/App.tsx`
- [x] T021 [US1] Set Agent 繁中 instructions in `apps/api/src/app/agent.py` (`以繁體中文回覆`)
- [x] T022 [US1] Handle AG-UI `RUN_ERROR` and network failures in `apps/web/src/lib/runtime.ts` with 繁中 error display (FR-008)
- [x] T023 [US1] Disable composer send while stream active in `apps/web/src/App.tsx` (double-submit guard)
- [x] T024 [US1] On mount in `apps/web/src/App.tsx`: call `GET ${VITE_API_BASE_URL}/v1/health`; if `status=degraded` show 繁中 error and disable composer (FR-011, no stub reply)
- [x] T025 [US1] Handle AbortError / connection drop in `apps/web/src/lib/runtime.ts`: stop streaming indicator, show 繁中「回覆未完成」, keep prior messages
- [x] T026 [P] [US1] Create `apps/web/src/lib/errors.ts` with unified error states (CONFIG, HEALTH_DEGRADED, NETWORK, STREAM_ABORT, MODEL_ERROR) mapped to 繁中 strings
- [x] T027 [US1] Wire `apps/web/src/lib/errors.ts` into `apps/web/src/App.tsx` and `apps/web/src/lib/runtime.ts`; extend quickstart scenario 3 step 6–7 for multi-turn FR-004a verification

**Checkpoint**: End-to-end chat with valid `OPENAI_API_KEY`; multi-turn context; health-degraded blocks chat

---

## Phase 4: User Story 2 — Confirm backend is reachable (Priority: P2)

**Goal**: `GET /v1/health` reports `healthy` with valid credentials, `degraded` when missing/invalid

**Independent Test**: `make health` or `curl /v1/health` — healthy with key, degraded without (spec SC-003, AC #2)

### Implementation for User Story 2

- [x] T028 [US2] Implement `apps/api/src/app/health.py` `GET /v1/health` matching `specs/001-agent-chat-app/contracts/health.openapi.yaml`
- [x] T029 [US2] Mount health router from `apps/api/src/app/health.py` in `apps/api/src/app/main.py`
- [x] T030 [US2] Add credential probe in `apps/api/src/app/health.py` (`model_credentials`: ok/missing/invalid; `model_reachable` probe)
- [x] T031 [US2] Return 503 JSON `ErrorResponse` from chat path when credentials missing before stream starts; document in `specs/001-agent-chat-app/contracts/ag-ui-boundary.md`
- [x] T032 [P] [US2] Add `apps/api/src/app/validation.py` to reject `messages[].content` longer than 4000 chars (data-model.md)
- [x] T033 [P] [US2] Add pure-function tests in `apps/api/tests/unit/test_health.py` for status derivation logic
- [x] T034 [P] [US2] Add integration test in `apps/api/tests/integration/test_health_endpoint.py` using httpx AsyncClient
- [x] T035 [P] [US1] Add `apps/api/tests/integration/test_agui_history.py`: mocked model asserts `messages[]` length ≥ 3 on second turn (FR-004a)
- [x] T036 [P] [US1] Add `apps/api/tests/integration/test_agui_stream.py`: TestClient POST `/agui` with mocked stream; assert AG-UI content events (Constitution V)

**Checkpoint**: Health endpoint and `/agui` boundary independently testable

---

## Phase 5: User Story 3 — Configurable backend URL (Priority: P2)

**Goal**: `VITE_API_BASE_URL` configures API base; unset/empty blocks chat with 繁中 error

**Independent Test**: Change env, restart web, chat hits new backend; unset env shows config error (spec SC-004, AC #3)

**⚠️ T040 depends on T018** (same file `apps/web/src/App.tsx`). T038–T039 may run in parallel with US1.

### Implementation for User Story 3

- [x] T037 [P] [US3] Implement `apps/web/src/lib/config.ts` reading `import.meta.env.VITE_API_BASE_URL` with trim/empty guard
- [x] T038 [US3] Create `apps/web/src/components/ConfigError.tsx` with 繁中 configuration error message
- [x] T039 [P] [US3] Add `apps/web/src/vite-env.d.ts` typing `VITE_API_BASE_URL` on `ImportMetaEnv`
- [x] T040 [US3] Gate `apps/web/src/App.tsx` — render `ConfigError` via `apps/web/src/lib/config.ts` and skip runtime when config invalid (**after T018**)

**Checkpoint**: No hardcoded backend URL; missing env blocks chat per clarification B

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Single-process serve, docs, edge cases, full quickstart validation

- [x] T041 Mount `apps/web/dist` via StaticFiles in `apps/api/src/app/main.py` for `make serve` single deployable
- [x] T042 [P] Create `.env.example` at repo root documenting `OPENAI_API_KEY`, `OPENAI_MODEL`, `VITE_API_BASE_URL`
- [x] T043 Update `README.md` with Makefile command index and link to `specs/001-agent-chat-app/quickstart.md`
- [x] T044 Add whitespace-only submit guard and `maxLength={4000}` with 繁中 message in `apps/web/src/components/assistant-ui/` composer
- [x] T045 Run all scenarios in `specs/001-agent-chat-app/quickstart.md`; verify no `*.db` session files created and Agent has no `db`/`tools` (SC-005, FR-010)

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 (Setup)
    └── Phase 2 (Foundational) ← BLOCKS all stories
            ├── Phase 3 (US1 — MVP chat)
            ├── Phase 4 (US2 — health + /agui tests)  ← parallel; US1 T024 needs T028–T030 for health gate
            └── Phase 5 (US3 — config)
                    └── Phase 6 (Polish)
```

**Note**: T024 (health gate on mount) requires T028–T030 deployed first, OR implement US2 before finishing US1 error paths.

### User Story Dependencies

| Story | Depends on | Independent test |
|-------|------------|------------------|
| **US1** (P1) | Phase 2; T028–T030 for T024 | Browser chat + streaming + multi-turn |
| **US2** (P2) | Phase 2 only | `curl /v1/health` + pytest |
| **US3** (P2) | Phase 2; **T040 after T018** | Env var swap test |

### Parallel Opportunities

**Phase 1**: T003–T006 [P]  
**Phase 2**: T008, T012, T013, T015 [P]  
**Post Phase 2**: US2 (T028–T036) parallel to US1 (T016–T027); US3 T037–T039 parallel; **T040 waits for T018**

---

## Implementation Strategy

### Demo MVP (streaming chat demo)

Phases 1–3 with manual `export VITE_API_BASE_URL=...` (T001–T027, plus T028–T030 if using T024 health gate).

1. Complete Phase 1 + Phase 2  
2. Complete Phase 3 (US1)  
3. **STOP and VALIDATE** — quickstart scenario 3  

### v1 Complete (all acceptance criteria)

Phases 1–5 (T001–T040) + Phase 6 (T041–T045) — covers AC #1–#3, FR-004a through FR-011.

---

## Notes

- Do **not** add Agno `db`, tools, RAG, MCP, scheduler, or auth in v1 (FR-010, research R10)
- Chat contract: `specs/001-agent-chat-app/contracts/ag-ui-boundary.md` (`POST /agui`)
- Health contract: `specs/001-agent-chat-app/contracts/health.openapi.yaml` (`GET /v1/health`)
- Acceptance health is `/v1/health`; AG-UI `/status` is auxiliary only
- Constitution **X**: every new repeatable action must appear in `Makefile`

---

## Task Summary

| Phase | Tasks | Story |
|-------|-------|-------|
| 1 Setup | T001–T006 (6) | — |
| 2 Foundational | T007–T015 (9) | — |
| 3 US1 MVP | T016–T027 (12) | US1 |
| 4 US2 Health + tests | T028–T036 (9) | US2/US1 |
| 5 US3 Config | T037–T040 (4) | US3 |
| 6 Polish | T041–T045 (5) | — |
| **Total** | **45 tasks** | |

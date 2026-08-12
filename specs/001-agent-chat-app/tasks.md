---
description: "Task list for Agent Chat App (001) — Agno AgentOS + assistant-ui"
---

# Tasks: Agent Chat App

**Input**: Design documents from `/specs/001-agent-chat-app/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Minimal backend tests for `/v1/health` only (plan R10 + spec AC #2). No frontend test framework in v1.

**Organization**: Tasks grouped by user story for independent implementation and validation.

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

- [ ] T001 Create `apps/api/src/app/` and `apps/web/src/` directory tree per specs/001-agent-chat-app/plan.md
- [ ] T002 Initialize `apps/api/pyproject.toml` with uv, Python 3.12, and `agno[os,agui]` dependencies
- [ ] T003 [P] Initialize `apps/web/package.json` with Vite, React 19, TypeScript, `@assistant-ui/react`, `@assistant-ui/react-ag-ui`
- [ ] T004 [P] Create root `Makefile` with `install`, `dev`, `build`, `test`, `lint`, `serve`, `health` targets per research.md R8
- [ ] T005 [P] Configure Ruff lint/format in `apps/api/pyproject.toml`
- [ ] T006 [P] Configure ESLint in `apps/web/eslint.config.js`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: AgentOS bootstrap, shared config/logging, web shell — **blocks all user stories**

**⚠️ CRITICAL**: No user story work until this phase completes

- [ ] T007 Implement `apps/api/src/app/config.py` for `OPENAI_API_KEY`, `OPENAI_MODEL`, `AGENT_OS_PORT`, static dist path
- [ ] T008 [P] Implement `apps/api/src/app/logging.py` structured JSON logger (`request_id`, `event`)
- [ ] T009 Implement `apps/api/src/app/agent.py` Agent factory — no `db`, tools, memory, or knowledge (research R10 guardrails)
- [ ] T010 Implement `apps/api/src/app/main.py` with AgentOS, `AGUI` interface, and CORS for Vite dev origin
- [ ] T011 Add `apps/api/src/app/__init__.py` and uvicorn entry `apps/api/src/app/main.py:app`
- [ ] T012 [P] Create `apps/web/index.html` and `apps/web/src/main.tsx` Vite React entry
- [ ] T013 [P] Create `apps/web/vite.config.ts` with `envPrefix: 'VITE_'` and dev server proxy optional note

**Checkpoint**: `uv run uvicorn` serves AgentOS with `POST /agui`; Vite shell loads blank React app

---

## Phase 3: User Story 1 — Send message and see streaming reply (Priority: P1) 🎯 MVP

**Goal**: User sends Traditional Chinese message; assistant reply streams incrementally in single thread

**Independent Test**: Open chat UI, send `請用三句話介紹你自己`, observe partial text before stream completes; send follow-up confirming context (spec SC-001, SC-002)

### Implementation for User Story 1

- [ ] T014 [P] [US1] Scaffold assistant-ui `Thread` and `Composer` into `apps/web/src/components/assistant-ui/`
- [ ] T015 [P] [US1] Implement `apps/web/src/lib/runtime.ts` using `@assistant-ui/react-ag-ui` with URL `${VITE_API_BASE_URL}/agui`
- [ ] T016 [US1] Implement `apps/web/src/App.tsx` with `AssistantRuntimeProvider` and single `Thread` (no ThreadList)
- [ ] T017 [P] [US1] Create `apps/web/src/i18n/zh-TW.ts` with 繁中 labels, empty-state, and streaming indicator strings
- [ ] T018 [US1] Apply 繁中 strings to `apps/web/src/components/assistant-ui/` and `apps/web/src/App.tsx`
- [ ] T019 [US1] Set Agent 繁中 instructions in `apps/api/src/app/agent.py` (`以繁體中文回覆`)
- [ ] T020 [US1] Handle AG-UI `RUN_ERROR` and network failures in `apps/web/src/lib/runtime.ts` with 繁中 error display
- [ ] T021 [US1] Disable composer send while stream active in `apps/web/src/App.tsx` (double-submit guard, spec edge case)

**Checkpoint**: End-to-end chat works with `OPENAI_API_KEY` set; multi-turn context via full history in AG-UI payload

---

## Phase 4: User Story 2 — Confirm backend is reachable (Priority: P2)

**Goal**: `GET /v1/health` reports `healthy` with valid credentials, `degraded` when missing/invalid

**Independent Test**: `make health` or `curl /v1/health` — healthy with key, degraded without (spec SC-003, AC #2)

### Implementation for User Story 2

- [ ] T022 [US2] Implement `apps/api/src/app/health.py` `GET /v1/health` matching `specs/001-agent-chat-app/contracts/health.openapi.yaml`
- [ ] T023 [US2] Mount health router from `apps/api/src/app/health.py` in `apps/api/src/app/main.py`
- [ ] T024 [US2] Add credential probe in `apps/api/src/app/health.py` (`model_credentials`: ok/missing/invalid; `model_reachable` probe)
- [ ] T025 [P] [US2] Add pure-function tests in `apps/api/tests/unit/test_health.py` for status derivation logic
- [ ] T026 [P] [US2] Add integration test in `apps/api/tests/integration/test_health_endpoint.py` using httpx AsyncClient

**Checkpoint**: Health endpoint independently verifiable without sending chat messages

---

## Phase 5: User Story 3 — Configurable backend URL (Priority: P2)

**Goal**: `VITE_API_BASE_URL` configures API base; unset/empty blocks chat with 繁中 error

**Independent Test**: Change env, restart web, chat hits new backend; unset env shows config error (spec SC-004, AC #3)

### Implementation for User Story 3

- [ ] T027 [P] [US3] Implement `apps/web/src/lib/config.ts` reading `import.meta.env.VITE_API_BASE_URL` with trim/empty guard
- [ ] T028 [US3] Create `apps/web/src/components/ConfigError.tsx` with 繁中 configuration error message
- [ ] T029 [US3] Gate `apps/web/src/App.tsx` — render `ConfigError` and skip runtime when config invalid
- [ ] T030 [P] [US3] Add `apps/web/src/vite-env.d.ts` typing `VITE_API_BASE_URL` on `ImportMetaEnv`

**Checkpoint**: No hardcoded backend URL; missing env blocks chat per clarification B

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Single-process serve, docs, edge cases, quickstart validation

- [ ] T031 Mount `apps/web/dist` via StaticFiles in `apps/api/src/app/main.py` for `make serve` single deployable
- [ ] T032 [P] Add request logging middleware in `apps/api/src/app/main.py` using `apps/api/src/app/logging.py`
- [ ] T033 [P] Create `.env.example` at repo root documenting `OPENAI_API_KEY`, `OPENAI_MODEL`, `VITE_API_BASE_URL`
- [ ] T034 Update `README.md` with Makefile command index and link to `specs/001-agent-chat-app/quickstart.md`
- [ ] T035 Add whitespace-only submit guard in `apps/web/src/components/assistant-ui/` composer (spec edge case)
- [ ] T036 Run all scenarios in `specs/001-agent-chat-app/quickstart.md` and fix any gaps found

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 (Setup)
    └── Phase 2 (Foundational) ← BLOCKS all stories
            ├── Phase 3 (US1 — MVP chat)
            ├── Phase 4 (US2 — health)     ← can parallel after Phase 2
            └── Phase 5 (US3 — config)     ← can parallel after Phase 2; integrates in App.tsx with US1
                    └── Phase 6 (Polish)   ← after desired stories complete
```

### User Story Dependencies

| Story | Depends on | Independent test |
|-------|------------|------------------|
| **US1** (P1) | Phase 2 | Browser chat + streaming |
| **US2** (P2) | Phase 2 only | `curl /v1/health` |
| **US3** (P2) | Phase 2; touches `App.tsx` after US1 | Env var swap test |

US2 is fully independent after Foundational. US3 can start after Foundational (T027–T030 parallel to US1) but T029 integrates with US1's `App.tsx`.

### Parallel Opportunities

**Phase 1**: T003–T006 all [P]  
**Phase 2**: T008, T012, T013 [P] after T001–T002  
**After Phase 2**:
- Track A: US1 (T014–T021) — MVP path
- Track B: US2 (T022–T026) — health API
- Track C: US3 (T027–T030) — config guard

**Phase 6**: T032, T033 [P]

### Parallel Example: Post-Foundational

```bash
# Developer A — MVP chat (US1)
T014 → T015 → T016 → T017 → T018 → T019 → T020 → T021

# Developer B — Health (US2, no UI dependency)
T022 → T023 → T024 → T025 → T026

# Developer C — Config (US3)
T027 → T028 → T029 → T030
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1 + Phase 2
2. Complete Phase 3 (US1)
3. **STOP and VALIDATE** — quickstart scenario 3 with real `OPENAI_API_KEY`
4. Demo streaming 繁中 chat

### Incremental Delivery

1. Setup + Foundational → AgentOS + AGUI live
2. **+ US1** → MVP demo (streaming chat)
3. **+ US2** → ops can `make health`
4. **+ US3** → configurable deployments
5. **+ Polish** → single-process `make serve`, docs

### Suggested MVP Scope

**Phases 1–3 only** (T001–T021) delivers core product value (spec P1).

---

## Notes

- Do **not** add Agno `db`, tools, RAG, MCP, scheduler, or auth in v1 (FR-010, research R10)
- Chat contract: `specs/001-agent-chat-app/contracts/ag-ui-boundary.md` (`POST /agui`)
- Health contract: `specs/001-agent-chat-app/contracts/health.openapi.yaml` (`GET /v1/health`)
- Commit after each phase checkpoint
- Constitution **X**: every new repeatable action must appear in `Makefile`

---

## Task Summary

| Phase | Tasks | Story |
|-------|-------|-------|
| 1 Setup | T001–T006 (6) | — |
| 2 Foundational | T007–T013 (7) | — |
| 3 US1 MVP | T014–T021 (8) | US1 |
| 4 US2 Health | T022–T026 (5) | US2 |
| 5 US3 Config | T027–T030 (4) | US3 |
| 6 Polish | T031–T036 (6) | — |
| **Total** | **36 tasks** | |

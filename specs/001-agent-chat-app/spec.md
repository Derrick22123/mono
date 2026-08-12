# Feature Specification: Agent Chat App

**Feature Branch**: `001-agent-chat-app`

**Created**: 2026-08-12

**Status**: Draft

**Input**: User description: "建立一個簡單的 agent chat app。使用者可在 web 介面輸入繁體中文訊息，並收到由 backend agent 串流回傳的回覆。v1 只需要單一聊天 thread；不包含登入、資料庫、RAG、tools、上傳附件或 production deployment。Acceptance criteria：1. web 介面可送出訊息並顯示串流回覆。2. backend 有可檢查的 health/status endpoint。3. 前端 endpoint 可透過 environment variable 設定。"

## Clarifications

### Session 2026-08-12

- Q: For v1 acceptance testing, how should the backend agent generate its streamed replies? → A: Real external model required (credentials via environment; chat fails clearly if missing)
- Q: For follow-up turns in the single thread, who should provide the prior conversation context to the model? → A: UI sends full thread history with every new message (backend stays conversation-stateless)
- Q: What should the health/status check report when the backend process is running but external model credentials are missing or invalid? → A: Degraded/unhealthy if model credentials are missing or invalid
- Q: If the frontend backend-location environment variable is unset or empty at startup, what should the web UI do? → A: Show a clear configuration error and block chat until the variable is set
- Q: What language should user-facing UI text use for errors, labels, and empty states in v1? → A: Traditional Chinese for all user-facing UI text

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Send a message and see a streaming reply (Priority: P1)

A visitor opens the chat web page, types a Traditional Chinese message into the
input, and sends it. They see their message appear in the single conversation
thread, then watch the agent's reply appear progressively (streaming) until the
reply is complete.

**Why this priority**: This is the entire product value of v1—without send +
streamed reply, nothing else matters.

**Independent Test**: Open the chat page, send one Traditional Chinese message,
and confirm the reply text appears incrementally until finished—no login or
other features required.

**Acceptance Scenarios**:

1. **Given** the chat page is open with an empty or existing single thread,
   **When** the user submits a non-empty Traditional Chinese message,
   **Then** the message appears in the thread and a streamed agent reply begins
   within a short, noticeable interval and completes as readable text.
2. **Given** a reply is currently streaming,
   **When** the user views the thread,
   **Then** partial reply content is visible before the stream ends (not only a
   final dump after completion).
3. **Given** the user has already exchanged messages in this session,
   **When** they send another message,
   **Then** it appends to the same single thread (no second thread is created),
   and the request includes the full ordered thread history so the agent can
   respond in context.

---

### User Story 2 - Confirm the backend is reachable (Priority: P2)

An operator or developer checks whether the backend that powers the chat agent
is up by calling a health/status check and receiving a clear healthy response.

**Why this priority**: Required for local verification and for the frontend (or
operators) to know the backend is available before relying on chat.

**Independent Test**: With the backend running, invoke the health/status check
and receive a successful healthy indication without sending a chat message.

**Acceptance Scenarios**:

1. **Given** the backend is running normally with valid model credentials,
   **When** someone requests the health/status check,
   **Then** the response indicates the service is healthy/available.
2. **Given** the backend process is running but model credentials are missing
   or invalid,
   **When** someone requests the health/status check,
   **Then** the response indicates degraded/unhealthy (not healthy/ready).
3. **Given** the backend is not running,
   **When** someone requests the health/status check,
   **Then** the check fails in an obvious way (no false "healthy" result).

---

### User Story 3 - Point the web UI at a configurable backend (Priority: P2)

A developer configures where the web UI should send chat requests by setting an
environment variable, then opens the UI and successfully chats against that
backend without changing application source code.

**Why this priority**: Enables local and alternate environments without
hardcoding; listed as an explicit v1 acceptance criterion.

**Independent Test**: Set the backend base location via environment variable to a
known running backend, load the UI, send a message, and receive a streamed
reply from that backend.

**Acceptance Scenarios**:

1. **Given** a valid backend location is set in the designated environment
   variable,
   **When** the user sends a chat message from the web UI,
   **Then** the UI uses that configured location (not a hardcoded alternate).
2. **Given** the backend-location environment variable is unset or empty when
   the UI loads,
   **When** the user opens the chat page,
   **Then** the UI shows a clear configuration error and blocks chat (send
   disabled or rejected) until a valid value is provided and the UI is
   reloaded/restarted as needed.
3. **Given** the environment variable is changed to another valid backend
   location and the UI is restarted/reloaded as required for config pickup,
   **When** the user sends a message,
   **Then** traffic goes to the newly configured location.

---

### Edge Cases

- Empty or whitespace-only submit: the UI MUST NOT send a chat request; the
  user remains on the same thread with a clear indication that input is
  required (or the send action stays disabled).
- Backend unreachable or health check failing while chatting: the UI MUST show
  a clear error state and MUST NOT pretend a reply is still streaming forever.
- Stream interrupted mid-reply (connection drop): the UI MUST stop the
  in-progress indicator and show that the reply did not complete; prior
  messages in the thread remain visible for the session.
- Very long user message or long agent reply: the thread remains usable
  (scrollable); the UI does not crash or freeze the page.
- Concurrent double-submit while a reply is streaming: the UI MUST prevent a
  second overlapping send (disable send or queue policy: reject second send
  until the current stream finishes).
- Backend-location environment variable unset or empty at UI load: the UI MUST
  show a clear configuration error and block chat until a valid value is set
  (no silent fallback to a default URL).
- External model credentials missing or invalid: chat MUST fail with a clear
  user-visible error (no fake/stubbed reply content); health/status MUST report
  degraded/unhealthy (not healthy/ready).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to open a web chat interface and view a single
  conversation thread.
- **FR-002**: Users MUST be able to enter Traditional Chinese text and submit it
  as a chat message.
- **FR-002a**: All user-facing UI text in v1 (errors, labels, empty states,
  configuration messages, and busy/streaming indicators) MUST be in Traditional
  Chinese.
- **FR-003**: The system MUST append the user's message to the single thread and
  return an agent reply as a progressive stream of text visible in that thread.
- **FR-004**: v1 MUST support exactly one chat thread per UI session (no thread
  list, create-thread, or switch-thread flows).
- **FR-004a**: For each new user message, the web UI MUST send the full ordered
  thread history (all prior user and agent messages in the session) with the
  request. The backend MUST NOT rely on server-side conversation storage in v1.
- **FR-005**: The backend MUST expose a health/status check that indicates
  whether the service is available for chat. The check MUST report
  degraded/unhealthy when model credentials are missing or invalid, even if the
  backend process is running.
- **FR-006**: The web UI's backend location MUST be configurable via an
  environment variable without requiring source code edits. If that variable is
  unset or empty at UI load, the UI MUST show a clear configuration error and
  block chat until a valid value is provided.
- **FR-007**: While a reply is streaming, the UI MUST show in-progress reply
  content and a clear busy/streaming state.
- **FR-008**: When the backend fails or the stream errors, the UI MUST show a
  user-visible error and end the busy/streaming state.
- **FR-009**: The product MUST NOT require user login or accounts in v1.
- **FR-010**: The product MUST NOT require a database, document retrieval (RAG),
  tool/function calling, file/attachment upload, or production deployment
  tooling in v1.
- **FR-011**: Agent replies MUST be generated by a real external model. Model
  credentials MUST be supplied via environment configuration. If credentials are
  missing or invalid, chat MUST fail clearly—v1 MUST NOT fall back to a
  deterministic stub or canned reply.

### Key Entities

- **Chat Thread**: The single conversation container for the session; holds an
  ordered sequence of messages; no multi-thread identity in v1. The UI retains
  thread state client-side and submits the full history on each send.
- **Message**: A user or agent utterance with role (user/agent), text content,
  and position in the thread order.
- **Streamed Reply**: An in-progress agent message whose text grows until the
  stream completes or fails.
- **Backend Availability**: The healthy/degraded/unhealthy status exposed by the
  health/status check, reflecting readiness to serve chat (including valid
  model credentials), not merely process uptime.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can open the chat page, send one Traditional Chinese
  message, and see a complete streamed agent reply in under 3 minutes on first
  try (including reading any minimal on-screen guidance).
- **SC-002**: During a successful reply, users can observe partial reply text
  before the full reply finishes in at least 90% of successful test sends
  (streaming is visible, not batch-only).
- **SC-003**: An operator can confirm backend chat readiness via the
  health/status check in under 30 seconds when the backend is running with valid
  model credentials; the same check reports degraded/unhealthy within 30 seconds
  when credentials are missing or invalid.
- **SC-004**: Changing only the documented environment variable (plus any
  required UI reload/restart) is sufficient to point the web UI at a different
  valid backend; no source edit is required—verified in a config-switch test.
- **SC-005**: 100% of the listed v1 out-of-scope capabilities (login, database,
  RAG, tools, uploads, production deployment) remain absent from the delivered
  user-facing flows.

## Assumptions

- Replies are plain text suitable for a chat bubble; rich media is out of scope.
- A specific model vendor/product name is left to planning, but v1 REQUIRES a
  real external model with environment-supplied credentials (no stub fallback).
- Acceptance of streaming chat assumes valid model credentials are configured in
  the test environment.
- Conversation context for follow-up turns is kept in the web UI for the
  session; each send includes the full ordered thread history. The backend is
  conversation-stateless in v1. Persistence across browser refresh or process
  restart is not required.
- "Environment variable" for the frontend backend location is set in the
  environment used to build or serve the web UI, consistent with common local
  web-app practice; exact variable name is left to planning/implementation docs.
  There is no built-in default URL—an unset or empty value MUST block chat with
  a visible configuration error.
- Traditional Chinese input is required; agent replies are expected to be
  intelligible chat text (Traditional Chinese preferred when the user writes in
  Traditional Chinese) but multilingual edge cases are not a v1 goal.
- All user-facing UI copy (errors, labels, empty states) MUST be Traditional
  Chinese in v1; operator/developer docs may use another language.
- A browser-based UI talking to a backend agent process is in scope as the
  minimal shape of this product; additional services, queues, or databases are
  out of scope (aligned with keeping distribution minimal for v1).
- No authentication means the chat endpoint is treated as a local/dev trust
  boundary only; hardening for public internet exposure is out of scope.
- Health/status reflects chat readiness, including valid model credentials;
  a running process alone is insufficient for a healthy result.

# Feature Specification: Agent Chat App

**Feature Branch**: `001-agent-chat-app`

**Created**: 2026-08-12

**Status**: Draft

**Input**: User description: "建立一個簡單的 agent chat app。使用者可在 web 介面輸入繁體中文訊息，並收到由 backend agent 串流回傳的回覆。v1 只需要單一聊天 thread；不包含登入、資料庫、RAG、tools、上傳附件或 production deployment。Acceptance criteria：1. web 介面可送出訊息並顯示串流回覆。2. backend 有可檢查的 health/status endpoint。3. 前端 endpoint 可透過 environment variable 設定。"

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
   **Then** it appends to the same single thread (no second thread is created).

---

### User Story 2 - Confirm the backend is reachable (Priority: P2)

An operator or developer checks whether the backend that powers the chat agent
is up by calling a health/status check and receiving a clear healthy response.

**Why this priority**: Required for local verification and for the frontend (or
operators) to know the backend is available before relying on chat.

**Independent Test**: With the backend running, invoke the health/status check
and receive a successful healthy indication without sending a chat message.

**Acceptance Scenarios**:

1. **Given** the backend is running normally,
   **When** someone requests the health/status check,
   **Then** the response indicates the service is healthy/available.
2. **Given** the backend is not running,
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
2. **Given** the environment variable is changed to another valid backend
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

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to open a web chat interface and view a single
  conversation thread.
- **FR-002**: Users MUST be able to enter Traditional Chinese text and submit it
  as a chat message.
- **FR-003**: The system MUST append the user's message to the single thread and
  return an agent reply as a progressive stream of text visible in that thread.
- **FR-004**: v1 MUST support exactly one chat thread per UI session (no thread
  list, create-thread, or switch-thread flows).
- **FR-005**: The backend MUST expose a health/status check that indicates
  whether the service is available.
- **FR-006**: The web UI's backend location MUST be configurable via an
  environment variable without requiring source code edits.
- **FR-007**: While a reply is streaming, the UI MUST show in-progress reply
  content and a clear busy/streaming state.
- **FR-008**: When the backend fails or the stream errors, the UI MUST show a
  user-visible error and end the busy/streaming state.
- **FR-009**: The product MUST NOT require user login or accounts in v1.
- **FR-010**: The product MUST NOT require a database, document retrieval (RAG),
  tool/function calling, file/attachment upload, or production deployment
  tooling in v1.

### Key Entities

- **Chat Thread**: The single conversation container for the session; holds an
  ordered sequence of messages; no multi-thread identity in v1.
- **Message**: A user or agent utterance with role (user/agent), text content,
  and position in the thread order.
- **Streamed Reply**: An in-progress agent message whose text grows until the
  stream completes or fails.
- **Backend Availability**: The healthy/unhealthy status exposed by the
  health/status check.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can open the chat page, send one Traditional Chinese
  message, and see a complete streamed agent reply in under 3 minutes on first
  try (including reading any minimal on-screen guidance).
- **SC-002**: During a successful reply, users can observe partial reply text
  before the full reply finishes in at least 90% of successful test sends
  (streaming is visible, not batch-only).
- **SC-003**: An operator can confirm backend availability via the
  health/status check in under 30 seconds when the backend is running.
- **SC-004**: Changing only the documented environment variable (plus any
  required UI reload/restart) is sufficient to point the web UI at a different
  valid backend; no source edit is required—verified in a config-switch test.
- **SC-005**: 100% of the listed v1 out-of-scope capabilities (login, database,
  RAG, tools, uploads, production deployment) remain absent from the delivered
  user-facing flows.

## Assumptions

- Replies are plain text suitable for a chat bubble; rich media is out of scope.
- Agent quality/model choice is out of scope for this specification; v1 assumes
  a backend agent that can accept a user message and stream text tokens/chunks.
- Conversation context for follow-up turns is kept for the lifetime of the UI
  session in the single thread; persistence across browser refresh or process
  restart is not required in v1.
- "Environment variable" for the frontend backend location is set in the
  environment used to build or serve the web UI, consistent with common local
  web-app practice; exact variable name is left to planning/implementation docs.
- Traditional Chinese input is required; agent replies are expected to be
  intelligible chat text (Traditional Chinese preferred when the user writes in
  Traditional Chinese) but multilingual edge cases are not a v1 goal.
- A browser-based UI talking to a backend agent process is in scope as the
  minimal shape of this product; additional services, queues, or databases are
  out of scope (aligned with keeping distribution minimal for v1).
- No authentication means the chat endpoint is treated as a local/dev trust
  boundary only; hardening for public internet exposure is out of scope.
- Health/status is a simple availability signal for the chat backend, not a deep
  dependency graph of third-party model providers (unless trivially included
  later in planning without expanding product scope).

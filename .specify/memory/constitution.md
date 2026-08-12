<!--
Sync Impact Report
- Version change: (unset/template) → 1.0.0
- Modified principles: template placeholders → ten decision-ready principles (I–X)
- Added sections: Domain Grounding; Review & Compliance Checklist
- Removed sections: none (template scaffold replaced in place)
- Follow-up TODOs: none
-->

# mono Constitution

## Core Principles

### I. Do Not Distribute by Default

**Rationale**: Coordination across processes is a tax paid in round trips,
failure modes, and operational surface area—not a latency optimization.
Vertical scale and a single deployable keep the working set and failure domain
understandable until evidence forces a split.

**Rule**: New code MUST ship as part of the existing single deployable unless a
written justification cites at least one of: working-set overflow, genuinely
independent compute, geographic latency, or organizational independence. Adding
a process, service, or queue without that justification is a constitution
violation. Measuring coordination cost in wall-clock milliseconds alone is
insufficient justification.

**How To Apply**: In review, reject PRs that introduce a new service boundary,
message queue, sidecar, or separate runtime without a linked ADR (or equivalent)
naming one allowed reason. Prefer vertical scaling, in-process modules, and
synchronous calls inside the monolith. If a split is approved, the ADR MUST
state the coordination tax accepted (extra hop, retry, consistency model).

### II. Optimize for Deletion, Not Extension

**Rationale**: Speculative abstractions outlive the problem they were meant to
solve and freeze the wrong shape into the codebase. Small, deletable modules
keep optionality; the wrong shared abstraction multiplies cost on every change.

**Rule**: A module MUST be small enough that one engineer can delete and rewrite
it in a day. Speculative abstractions are forbidden. Inline until duplication
hurts; extract only at the third occurrence of the same concrete pattern.
Duplication of fewer than three occurrences MUST be preferred over introducing a
shared abstraction.

**How To Apply**: Reject new base classes, generic frameworks, plugin systems, or
"future-proof" interfaces that have fewer than three concrete call sites today.
When reviewing size, ask whether the owning engineer could rewrite the module in
one day; if not, require a split or simplification before merge.

### III. Make Dependencies Explicit

**Rationale**: Hidden coupling and import-time side effects make behavior
non-local. Explicit dependencies turn review into a checklist and keep tests
honest about what they exercise.

**Rule**: A reader MUST be able to see every dependency of a function in its
signature or at the top of its file. Hidden coupling, implicit global state, and
import-time side effects are forbidden. Prefer dependency injection over
singletons. New singletons or ambient globals that mutate shared state are a
violation unless confined to the process entrypoint and passed downward
explicitly.

**How To Apply**: Reject PRs that read config, clients, or request context from
module-level mutable globals inside business logic; require parameters or
constructor injection. Reject modules whose import executes network I/O, starts
threads, or mutates process-wide registries. File-top imports and function
signatures are the dependency inventory—review them as such.

### IV. Contract at the Boundary, Not in the Middle

**Rationale**: Cross-context meaning must be reconciled where ownership is clear.
Shared mutable schemas in the middle of the stack create silent cross-team
breakage and unclear version ownership.

**Rule**: Every producer/consumer boundary (HTTP, queue, file, database) MUST
have a versioned schema. Semantic reconciliation MUST happen at the boundary and
MUST be owned by the side that understands both contexts. Shared mutable schemas
(one evolving definition silently consumed by multiple unversioned parties) are
forbidden.

**How To Apply**: For any new or changed boundary, require a named schema artifact
with an explicit version (e.g., OpenAPI/JSON Schema/Protobuf/Avro/SQL migration
version). Reject PRs that pass ad-hoc dicts across process or storage boundaries
without a schema, or that mutate a "shared types" package in place without a
version bump and compatibility plan. Ownership of translation belongs at the
adapter, not deep in domain logic.

### V. Test the Transformation, Not the Plumbing

**Rationale**: Plumbing tests that reassert framework behavior create noise
without catching product bugs. Pure transformations are cheap to unit-test;
boundaries need integration coverage against real contracts.

**Rule**: Unit tests MUST cover pure transformation logic. Integration tests MUST
cover boundaries. Do not mock what you own; do mock what you do not. A CI run is
not green for a bugfix unless it includes a failing-then-passing test that
reproduces that bug.

**How To Apply**: Reject unit tests that primarily assert HTTP framework routing,
ORM boilerplate, or mocked collaborators you own end-to-end. Prefer testing pure
functions/modules for domain transforms, and integration tests for HTTP, queue,
file, and database boundaries. For bugfix PRs, require a regression test that
failed before the fix; merge without that test is a violation.

### VI. Emit Structured Events, Derive Everything Else

**Rationale**: Disconnected logs, metrics, and traces invent three incomplete
truths. One structured event stream with high-cardinality identity fields lets
observability be projected rather than hand-maintained.

**Rule**: New code MUST emit structured events as the observability primitive.
Logs, metrics, and traces are projections of those events—not independent
channels with divergent fields. High-cardinality fields (user id, request id,
tenant id, feature flag state) are required when applicable to the event, not
optional. Unstructured log lines in new code are forbidden.

**How To Apply**: Reject `print`/string-only logging in new or touched paths.
Require event payloads as structured key/value (or equivalent) including request
id and, when in scope, user id, tenant id, and active feature flag state. New
dashboards and alerts MUST derive from the same event fields rather than
introducing parallel ad-hoc log formats.

### VII. Recovery over Prevention

**Rationale**: Prevention without recovery couples uptime to perfect foresight.
Fast, practiced rollback turns incidents into short blips; irreversible deploys
turn every change into a bet the team cannot unwind.

**Rule**: Every change MUST be revertible in under five minutes without a code
change. Feature flags MUST gate risky paths. Schema and data migrations MUST use
expand-then-contract. Rollback MUST be tested as part of the deploy procedure,
not assumed.

**How To Apply**: Reject migrations that drop/rename columns or change meanings
in the same deploy that removes old readers/writers. Require expand (additive)
then contract (removal) across deploys. Risky behavior needs a flag defaulting
to off or safely ramped. Deploy docs/scripts MUST include a rollback step that
has been executed in staging or a dry-run; "we can revert the commit" alone does
not satisfy the five-minute, no-code-change bar when traffic is live.

### VIII. Attention Is Finite

**Rationale**: Pages without user impact train teams to ignore signals. Decorative
dashboards and zombie alerts consume the only scarce resource in operations:
human attention.

**Rule**: Every alert MUST correspond to a user-visible symptom and MUST link to
a runbook. Dashboards are saved queries for investigation, not decoration.
Signals that have not produced a useful page in 90 days MUST be deleted or
explicitly rejustified in writing.

**How To Apply**: Reject new alerts that fire on internal utilization alone
without a mapped user symptom (error, latency, correctness, availability).
Require a runbook URL/path in the alert definition. In review of observability
PRs, delete or schedule deletion of alerts/dashboards idle for 90+ days unless
an owner documents why they remain.

### IX. Value Is Realized at the User, Not at Merge

**Rationale**: Merge is an internal milestone. Users experience deployed,
observable, revertible behavior—anything less is inventory risk, not delivery.

**Rule**: A PR is not done until the change is in users' hands, observable, and
revertible. "Shipped" means deployed, instrumented, and monitored—not merged.

**How To Apply**: Do not close delivery work at merge-only status. Require
evidence of deploy (or equivalent release path), instrumentation covering the
change (structured events/metrics), and a rollback path before calling the work
shipped. Reviews MUST flag missing instrumentation or rollback as blocking for
user-facing changes.

### X. Commands Are Discoverable; Local Dev Matches CI

**Rationale**: Hidden CI-only steps and undocumented targets recreate
environment drift. A single named command surface is the interface of the
engineering system; if newcomers cannot list it quickly, the interface is
broken.

**Rule**: Every repeatable action (build, test, lint, migrate, deploy, seed) MUST
be a single named command listed in one place and runnable with no hidden
arguments. The command a developer runs locally MUST be the same command CI
runs. CI-only shell steps, undocumented makefile/task targets, and
"works on my machine" gaps are forbidden. If a new contributor cannot list every
command in 30 seconds from the documented command index, the interface is
broken and MUST be fixed.

**How To Apply**: Reject PRs that add CI workflow steps invoking scripts or flags
not exposed via the project's command index (e.g., Taskfile/Makefile/`just`/
package scripts README section—one canonical list). Local README "also run X
with flag Y" that CI does not run is a violation; unify them. New repeatable
actions MUST add one named entry to the index in the same PR.

## Domain Grounding

These principles are first-principles constraints across five domains. They are
not aspirational tone; each maps to falsifiable review checks above.

| Domain | Primary principles | First-principles pressure |
| --- | --- | --- |
| Distributed systems | I, IV, VII | Minimize coordination; version boundaries; prefer recoverable failure |
| Software design | II, III, X | Deletable modules; explicit dependencies; discoverable interfaces |
| Data engineering | IV, V, VII | Versioned contracts; test transforms; expand-then-contract evolution |
| DevOps | VII, IX, X | Rehearsed rollback; ship means production; local ≡ CI |
| Observability | VI, VIII, IX | Structured events as source of truth; scarce attention; instrument what ships |

Cross-domain conflicts resolve toward the tighter operational constraint: prefer
non-distribution (I), recoverability (VII), and user-visible proof (IX) over
convenience abstractions.

## Review & Compliance Checklist

Reviewers MUST be able to point at a diff and name a violated principle without
interpretation. Use this checklist on every PR:

1. New process/service/queue without allowed justification? → **I**
2. Speculative abstraction or extract-before-third-use? → **II**
3. Hidden globals, import side effects, unclear deps? → **III**
4. Boundary without versioned schema / shared mutable schema? → **IV**
5. Plumbing-only tests, mocking owned code, bugfix without regression test? → **V**
6. Unstructured logs or missing required high-cardinality fields? → **VI**
7. Non-revertible change, missing flag, unsafe migration, untested rollback? → **VII**
8. Alert without user symptom/runbook, or zombie signal retained? → **VIII**
9. Called "done" at merge without deploy, instrumentation, monitoring? → **IX**
10. CI-only steps or commands missing from the single command index? → **X**

## Governance

This constitution supersedes informal team habit and conflicting guidance in
docs or chat. Ambiguity in other documents resolves in favor of these rules.

Amendments MUST be proposed as a PR that updates `.specify/memory/constitution.md`,
includes a Sync Impact Report (version delta, principle changes, TODOs), and
states the semantic version bump:

- **MAJOR**: Removal or incompatible redefinition of a principle
- **MINOR**: New principle/section or materially expanded obligation
- **PATCH**: Clarification, wording, or non-semantic refinement

Compliance is verified in code review using the Review & Compliance Checklist.
Complexity and new distributed surfaces require written justification (ADR or
equivalent) referenced from the PR. Waivers are temporary, written, time-bounded,
and MUST name the principle waived and the expiry date.

Runtime planning and implementation specs MUST read this file and treat
violations as blocking unless a recorded waiver exists.

**Version**: 1.0.0 | **Ratified**: 2026-08-12 | **Last Amended**: 2026-08-12

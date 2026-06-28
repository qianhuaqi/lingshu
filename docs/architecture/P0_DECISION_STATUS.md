# P0 Architecture Decision Status

- Status: Active P0 control document
- Parent Issue: #25
- Active decision Issue: #34
- Active proposal: P0-D2 / ADR-002
- Last accepted decision: P0-D1 / ADR-001 / PR #32
- Last updated: 2026-06-28

## Authority

`LINGSHU_FRAMEWORK_BLUEPRINT.md` is the single overall architecture document. This file records decision state only.

- **Confirmed** may be used by a later implementation Issue.
- **Proposed** and **Candidate** must not be implemented.
- **Rejected** must not be reintroduced without a new Issue, ADR, and project-lead approval.

## Confirmed

### Project identity

- LingShu is a new, independently implemented Python Web/API framework.
- It is not based on Sanic, FastAPI, Flask, Django, Starlette, or another upper-level Web framework.
- The archived implementation creates no compatibility obligation.
- Production framework code will be written from scratch.

### Framework ownership

LingShu defines and controls its own application kernel, HTTP runtime, native server behavior, request/response model, routing, middleware, lifecycle, cancellation, cleanup, extension protocol, CLI, and ecosystem.

Their physical package placement remains unresolved.

### Single repository and development concurrency

- Canonical repository: `qianhuaqi/lingshu`.
- ADR-001 is accepted; Issue #31 is completed; PR #32 is merged.
- Core, official capabilities, tests, documentation, tooling, and release metadata remain in this repository unless a future ADR proves otherwise.
- Concurrent tasks use separate Issues, writer-prefixed branches, primary writers, worktrees or clones, virtual environments, and Pull Requests.
- Write scopes must not overlap.
- Shared contracts merge before dependent work.
- Development may be parallel; integration into `main` is serial.

### Repository reset and compatibility

- Legacy implementation: `archive/legacy-sanic-20260628` at `b869270e0ec7cbc324d17ef246e39d0873aab14f`.
- Archived source, tests, dependencies, Issues, and PRs are historical reference only.
- No Sanic adapter, migration layer, or legacy API forwarding package is required before v1.0.

### P0 gate and request auditability

- P0 permits architecture and governance work only.
- No production package, directory skeleton, runtime dependency, or implementation phase may start before P0 acceptance.
- Every accepted business request has an internal Request ID and bounded, redacted, recoverable Runtime Record.

## Proposed — P0-D2, not executable

Issue #34 and ADR-002 propose:

- standard-library `asyncio` semantics as the correctness baseline;
- one event loop and one application runtime per Worker process;
- Supervisor-managed Workers with bounded restart and crash-loop stop;
- explicit Supervisor → Worker → Application → Connection → Request → Operation ownership;
- request-owned tasks by default and explicitly registered application-owned background tasks;
- no unregistered fire-and-forget tasks;
- one active request at a time per HTTP/1.1 connection, with concurrency across connections;
- hierarchical bounded admission and bounded waiters;
- end-to-end backpressure across transports, bodies, routes, executors, dependencies, telemetry, and Runtime Records;
- absolute monotonic Deadline propagation without nested timeout reset;
- explicit cancellation reasons and parent-to-child cancellation;
- bounded thread and process executors for blocking and CPU-heavy work;
- ordered, bounded graceful shutdown and hard-stop escalation;
- context isolation, observability, leak gates, and concurrency stress tests.

Proposal documents:

- `docs/decisions/ADR-002-runtime-concurrency-model.md`
- `docs/architecture/RUNTIME_CONCURRENCY_MODEL.md`

Merging the decision PR confirms these semantics. Until then they remain Proposed.

## Rejected

- LingShu as a Sanic template or adapter.
- Migration of the old runtime into the new source tree.
- Legacy compatibility shims without released consumers.
- Archived tests as acceptance tests for the new framework.
- Continuing old C0/C1/C2 or R1-R6 roadmaps.
- Separate repositories for initial Core, HTTP, Server, Record, or official capabilities.
- Multiple developers sharing one writable directory or one branch.
- Parallel branches changing the same public contract or write scope.
- Long-lived shared `develop` branch.
- Automatic merge of concurrent Pull Requests.

## Candidate — not executable

### Packaging and source layout

- one distribution versus multiple distributions;
- `packages/` or another repository root layout;
- direct `lingshu/` versus `src/<package>/`;
- exact Core, HTTP, Server, Record, CLI, testing, resource, and extension directories;
- one versus multiple `pyproject.toml` files.

### Component and extension boundaries

- Core, HTTP, Server, and Record as internal modules versus separate distributions;
- exact dependency direction and public exports;
- Runtime Record default installation status;
- WebSocket, OpenAPI, and Observability placement;
- Auth, Tenant, RBAC, Data, SQL, database drivers, Redis, Cache, i18n, Resilience, Scheduler, and Storage boundaries.

### Deferred by P0-D2

- minimum Python version;
- exact public Scope, Deadline, limiter, and cancellation API names;
- exact numeric defaults;
- mandatory third-party event loop or parser;
- listener socket distribution strategy;
- HTTP/2 and HTTP/3 multiplexing;
- physical module and distribution placement.

### Release and public governance

- P1 and v0.x mapping;
- Python and platform support matrix;
- first public package release point;
- v1.0 API freeze scope;
- License, contribution policy, vulnerability reporting, supported security versions, changelog policy, and code of conduct.

## Pending hardening consolidation

Before P0 acceptance, accepted requirements from `P0_HARDENING_CHECKLIST.md` must enter the Blueprint: time model, identifiers, exceptions, configuration versioning and reload, serialization, async context isolation, telemetry fields, and Worker/storage budgets.

## Confirmation rule

A proposal or candidate becomes Confirmed only after:

1. a dedicated Issue;
2. a Blueprint amendment or ADR;
3. explicit project-lead confirmation;
4. reviewed and merged Pull Request;
5. this register is synchronized.

P1 remains blocked until all P0 exit conditions are met.

# P0 Architecture Decision Status

- Status: Active P0 control document
- Parent Issue: #25
- Active decision Issue: none
- Last accepted decision: P0-D2 / ADR-002 / PR #35
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

### Single repository and development concurrency — P0-D1

- Canonical repository: `qianhuaqi/lingshu`.
- ADR-001 is accepted; Issue #31 is completed; PR #32 is merged.
- Core, official capabilities, tests, documentation, tooling, and release metadata remain in this repository unless a future ADR proves otherwise.
- Concurrent tasks use separate Issues, writer-prefixed branches, primary writers, worktrees or clones, virtual environments, and Pull Requests.
- Write scopes must not overlap.
- Shared contracts merge before dependent work.
- Development may be parallel; integration into `main` is serial.

### Runtime concurrency — P0-D2

- ADR-002 is accepted.
- Issue #34 is completed.
- PR #35 merged at `6809a18b0284d18fd1ee46d9af7183521a66d67c`.
- Detailed model: `docs/architecture/RUNTIME_CONCURRENCY_MODEL.md`.

Confirmed semantics:

- standard-library `asyncio` behavior is the correctness baseline;
- each Worker process owns one event loop and one Application Runtime;
- Supervisor manages Worker readiness, signals, bounded restart, and exit;
- Workers do not share mutable Python application state;
- runtime ownership is Supervisor → Worker → Application → Connection → Request → Operation;
- request-created tasks are request-owned by default;
- long-lived tasks require explicit Application or Worker registration;
- unregistered fire-and-forget tasks are prohibited;
- one HTTP/1.1 connection executes one request at a time, while connections run concurrently;
- admission, waiters, queues, buffers, executors, dependencies, telemetry, and Runtime Records are bounded;
- backpressure propagates through the entire request/response pipeline;
- Deadline is absolute and monotonic and is not reset by nested calls;
- cancellation reasons are explicit and propagate from owner to children;
- blocking and CPU-heavy work is isolated from the event loop through bounded mechanisms;
- Worker restart is bounded and crash loops stop;
- shutdown drains, cancels, cleans up, flushes, and escalates to hard stop;
- request and operation context is Scope-local;
- concurrency, overload, cancellation, leak, race, deadlock, and shutdown tests are mandatory.

### Repository reset and compatibility

- Legacy implementation: `archive/legacy-sanic-20260628` at `b869270e0ec7cbc324d17ef246e39d0873aab14f`.
- Archived source, tests, dependencies, Issues, and PRs are historical reference only.
- No Sanic adapter, migration layer, or legacy API forwarding package is required before v1.0.

### P0 gate and request auditability

- P0 permits architecture and governance work only.
- No production package, directory skeleton, runtime dependency, or implementation phase may start before P0 acceptance.
- Every accepted business request has an internal Request ID and bounded, redacted, recoverable Runtime Record.

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
- One thread per request.
- Unbounded fire-and-forget tasks, executor queues, or waiter lists.
- Global mutable request context.
- Resetting the full timeout at every nested layer.
- Concurrent HTTP/1.1 request execution on one connection in the initial runtime.
- Infinite Worker restart loops.
- Shutdown without draining and cleanup.
- Requiring a third-party event loop for correctness.

## Candidate — not executable

### Recommended next decision: P0-D3 packaging and source layout

- one distribution versus multiple distributions;
- `packages/` or another repository root layout;
- direct `lingshu/` versus `src/lingshu/`;
- one versus multiple `pyproject.toml` files;
- physical boundaries for Core, HTTP, Server, Record, CLI, Testing, and Extensions;
- public imports and dependency direction;
- placement of tests, examples, tools, templates, benchmarks, protocol tests, and fuzzing assets.

### Component and extension details

- Runtime Record default installation and storage placement;
- WebSocket, OpenAPI, and Observability placement;
- Auth, Tenant, RBAC, Data, SQL, database drivers, Redis, Cache, i18n, Resilience, Scheduler, and Storage boundaries.

### Deferred by P0-D2

- minimum supported Python version;
- public Scope, Deadline, limiter, and cancellation API names;
- exact numeric defaults;
- mandatory third-party event loop or parser;
- listener socket distribution strategy;
- HTTP/2 and HTTP/3 multiplexing.

### Release and public governance

- P1 and v0.x mapping;
- Python and platform support matrix;
- first public package release point;
- v1.0 API freeze scope;
- License, contribution policy, vulnerability reporting, supported security versions, changelog policy, and code of conduct.

## Pending hardening consolidation

P0-D2 integrated monotonic Deadline, Async Context isolation, bounded Worker/connection/queue semantics, and part of the Telemetry requirements into the Blueprint.

Before P0 acceptance, remaining accepted hardening requirements must be integrated: identifier standards, exception semantics, configuration versioning and reload, serialization rules, Runtime Record storage budgets, and disk policy.

## Confirmation rule

A proposal or candidate becomes Confirmed only after:

1. a dedicated Issue;
2. a Blueprint amendment or accepted ADR;
3. explicit project-lead confirmation;
4. reviewed and merged Pull Request;
5. this register is synchronized.

P1 remains blocked until all P0 exit conditions are met.

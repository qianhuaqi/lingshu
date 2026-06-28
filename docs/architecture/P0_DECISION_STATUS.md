# P0 Architecture Decision Status

- Status: Active P0 control document
- Parent Issue: #25
- Active decision Issue: none
- Last accepted decision: P0-D4 / ADR-004 / PR #41
- Last updated: 2026-06-28

## Authority

`LINGSHU_FRAMEWORK_BLUEPRINT.md` is the single overall architecture document. This file records decision state only.

- **Confirmed** decisions may be used by later implementation Issues.
- **Proposed** and **Candidate** decisions must not be implemented.
- **Rejected** decisions require a new Issue, ADR, and project-lead approval before reconsideration.

## Confirmed

### Project identity

- LingShu is a new, independently implemented Python Web/API framework.
- It is not based on another upper-level Web framework.
- The archived implementation creates no compatibility obligation.
- Production framework code will be written from scratch.

### P0-D1: Repository and development concurrency

- Canonical repository: `qianhuaqi/lingshu`.
- One Issue, writer branch, primary writer, isolated worktree/environment, and Pull Request per concurrent task.
- Non-overlapping write scopes and provider-first integration.
- Parallel development with serial integration into `main`.

### P0-D2: Runtime concurrency

- Standard-library `asyncio` behavior is the correctness baseline.
- One event loop and Application Runtime per Worker.
- Structured Supervisor → Worker → Application → Connection → Request → Operation ownership.
- Request-owned child tasks and no unregistered fire-and-forget tasks.
- One active HTTP/1.1 request per connection.
- Bounded admission, queues, executors, telemetry, and Runtime Records.
- Absolute monotonic Deadline and cancellation propagation.
- Blocking-work isolation, bounded Worker restart, and ordered graceful shutdown.

### P0-D3: Package and component layout

```text
Repository:      qianhuaqi/lingshu
Distribution:    lingshu
Import package:  lingshu
Packaging file:  pyproject.toml
Production code: lingshu/
src layout:      prohibited
```

Confirmed direction:

```text
runtime     → core
http        → runtime + core
server      → http + runtime + core
record      → core + stable runtime contracts
extensions  → core + runtime (+ documented HTTP contracts when required)
cli         → public composition surface
testing     → public/test-support surfaces
```

Additional rules:

- one framework version and release cadence;
- no initial component distributions;
- no dependency cycles;
- production does not depend on `testing`;
- controlled root public facade;
- lazy optional integrations;
- default Runtime Record mechanisms with optional heavy exporters;
- wheel and sdist isolated-install quality gate.

### P0-D4: Application Kernel and request pipeline

- ADR-004 accepted.
- Issue #40 completed.
- PR #41 merged at `bb78918dc2bc92dd49c34258e3707abd37274f12`.
- Detailed model: `docs/architecture/APPLICATION_KERNEL_AND_REQUEST_PIPELINE.md`.

Confirmed semantics:

- public `LingShu` composition root and private low-level Application Kernel;
- lifecycle `CREATED → CONFIGURING → FROZEN → STARTING → RUNNING → DRAINING → STOPPING → STOPPED`;
- registration only before freeze;
- immutable Application Revision and atomic compiled-plan publication;
- no partial plan after freeze failure;
- immutable compiled Router and deterministic conflict validation;
- asynchronous Handler with one explicit Request;
- deterministic application and route Middleware onion ordering;
- single-use Scope-bound `call_next`;
- fixed request pipeline from protocol acceptance through Scope cleanup;
- immutable Request metadata, scoped state, and bounded single-consumer body;
- exactly-once Handler return normalization;
- `Response`, `str`, and bytes-like initial Handler results;
- `None`, tuple magic, arbitrary iterators, and unknown values rejected by default;
- Response states `NEW → PREPARED → COMMITTED → COMPLETED/ABORTED`;
- no status/header mutation or replacement response after commit;
- exception resolution through route mapper, application mapper, `HTTPException`, then safe default before commit;
- extensions compiled before startup and immutable during request processing;
- root public exports `LingShu`, `Request`, `Response`, and `HTTPException`;
- state-machine, ordering, ownership, commit, error, leak, and import-side-effect tests required.

### Repository reset, compatibility, and P0 gate

- Legacy implementation is historical reference only.
- No Sanic adapter, migration layer, or legacy API forwarding package is required before v1.0.
- P0 permits architecture and governance only.
- No production package, source tree, runtime dependency, or implementation phase begins before P0 acceptance.
- Every accepted request has an internal Request ID and bounded, redacted, recoverable Runtime Record.

## Rejected

- upper-level Web framework dependency;
- legacy runtime migration or compatibility shims without released consumers;
- separate initial repositories or distributions;
- shared writable worktrees, multi-writer branches, automatic merge, or long-lived `develop`;
- unbounded tasks, queues, executors, waiters, or mutable global request state;
- one thread per request;
- resetting timeout at every nested layer;
- concurrent HTTP/1.1 requests on one connection in the initial runtime;
- infinite Worker restart loops or shutdown without drain/cleanup;
- mandatory third-party event loop for correctness;
- `src/lingshu/`, initial `packages/`, component-level packaging, or component versions;
- production dependency on `lingshu.testing`;
- treating all deep imports as public;
- editable-only packaging evidence;
- running registry mutation or import-time registration;
- route conflict resolution by registration order;
- unordered Middleware or multiple `call_next` calls;
- implicit sync Handler execution on the event loop;
- implicit tuple or `None` response magic;
- mutable Request metadata;
- multiple Response commits or replacement after commit;
- per-request mutation of the compiled plan.

## Candidate — not executable

### Recommended next decision: P0-D5 hardening foundations

- identifier formats and correlation for Request, Connection, Trace, Operation, Worker, Revision, and Runtime Record;
- exception taxonomy, stable error codes, safe client messages, redaction, and cause chains;
- configuration sources, precedence, validation, immutability, versioning, reload, and rollback;
- JSON/general serialization and content-negotiation baseline;
- Runtime Record event envelope, file/storage format, budgets, retention, disk safety, failure mode, and crash recovery;
- common telemetry fields and correlation requirements.

### Deferred by P0-D4

- automatic HEAD/OPTIONS;
- host routing, reverse routing, mounts, and sub-applications;
- cookies, forms, multipart, uploads, and advanced body APIs;
- public run/serve and CLI semantics;
- sync Handler adaptation;
- dependency injection;
- exact numeric limits, timeouts, and media-type defaults.

### Official capabilities and protocols

- Auth, Tenant, Tenant-Auth bridge, RBAC;
- Data, SQL, database drivers, Redis, Cache;
- i18n, OpenAPI, Observability, Resilience;
- Scheduler, Storage, WebSocket;
- HTTP/2, HTTP/3, and optional accelerators.

### Support, packaging implementation, and governance

- minimum Python version and platform matrix;
- build backend and authoritative version source;
- optional extras and official integration catalog;
- P1/v0.x mapping and first public release;
- v1.0 API freeze scope;
- License, contribution policy, vulnerability reporting, supported security versions, changelog policy, and code of conduct.

## Confirmation rule

A proposal or candidate becomes Confirmed only after:

1. a dedicated Issue;
2. a Blueprint amendment or accepted ADR;
3. explicit project-lead confirmation;
4. reviewed and merged Pull Request;
5. this register is synchronized.

P1 remains blocked until all P0 exit conditions are met.

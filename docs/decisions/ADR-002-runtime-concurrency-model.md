# ADR-002: Runtime concurrency, task ownership, and graceful shutdown

- Status: Accepted
- Date: 2026-06-28
- Parent architecture Issue: #25
- Decision Issue: #34 (completed)
- Implemented by: PR #35
- Effective merge commit: `6809a18b0284d18fd1ee46d9af7183521a66d67c`
- Detailed model: `docs/architecture/RUNTIME_CONCURRENCY_MODEL.md`

## Context

LingShu must process many connections and requests concurrently without unbounded queues, request-context leakage, orphan tasks, blocked event loops, cancellation loss, or shutdown corruption.

This ADR fixes the runtime-concurrency semantics. It does not decide the final source directory, distribution layout, minimum Python version, HTTP/2 or HTTP/3 multiplexing, listener distribution strategy, or a mandatory third-party event loop.

## Decision

### 1. Asynchronous baseline

Python standard-library `asyncio` semantics are the correctness baseline.

LingShu must run correctly without a third-party event loop. Any future optional accelerator requires a separate ADR and must preserve the same observable behavior.

### 2. Worker and event-loop model

Each Worker process owns exactly one event loop and one application runtime.

A Supervisor may manage one or more Workers. Workers do not share mutable Python application state. Cross-Worker coordination requires an explicit IPC, database, cache, message, or operating-system mechanism.

Single-Worker execution is the semantic reference. Multi-Worker execution scales throughput without changing request, cancellation, shutdown, extension, or Runtime Record semantics.

### 3. Structured ownership

Every task belongs to an explicit Scope:

```text
Supervisor
└─ Worker
   └─ Application Runtime
      ├─ Listener and infrastructure tasks
      ├─ Application-owned background tasks
      └─ Connection
         └─ Request
            └─ Operation and child tasks
```

A child Scope cannot outlive its owner unless ownership is explicitly transferred through a reviewed framework API.

Unregistered fire-and-forget tasks are prohibited.

### 4. Request and background tasks

Tasks created during request handling are request-owned by default.

When a request completes, times out, disconnects, or is cancelled, remaining request-owned tasks are cancelled and awaited within a bounded cleanup budget.

Long-lived background work must be explicitly registered as application-owned or Worker-owned and declare its name, owner, start phase, stop policy, failure policy, restart policy, Deadline, and shutdown behavior.

Detached background tasks start with a clean request context unless safe values are explicitly copied.

### 5. HTTP/1.1 concurrency

One HTTP/1.1 connection executes at most one request at a time.

Multiple connections execute concurrently. Keep-alive requests on one connection are processed sequentially. LingShu does not concurrently execute pipelined HTTP/1.1 requests or emit responses out of order.

Read-ahead buffering is bounded. HTTP/2 and HTTP/3 multiplexing require separate decisions.

### 6. Hierarchical admission and backpressure

Concurrency is bounded at multiple layers, including Worker connections, active requests, application and route limits, background tasks, executors, outbound dependencies, telemetry, and Runtime Record queues.

Waiting queues are bounded and have a maximum wait Deadline. Capacity exhaustion produces backpressure or explicit rejection; it never creates an unbounded waiter list.

Transport reads, request-body streaming, response streaming, parser buffers, executors, dependencies, telemetry, and Runtime Records participate in end-to-end backpressure.

Slow clients cannot reserve unlimited Worker resources.

### 7. Deadline model

Timeout budgeting uses an absolute monotonic Deadline.

A child operation receives the same Deadline or an earlier one. It never receives a fresh copy of the original duration. Queueing, middleware, route handling, extensions, database/cache calls, outbound calls, streaming, and cleanup consume the remaining budget.

Wall-clock time is used for human-readable timestamps, not timeout measurement.

### 8. Cancellation

Cancellation carries an explicit reason, including client disconnect, request Deadline, server draining, Worker stopping, parent cancellation, application cancellation, and admission failure.

Cancellation propagates from owner to children. Code may perform bounded cleanup but must not silently swallow cancellation and continue normal request work.

Shielding is allowed only for narrow, bounded, documented cleanup or commit sections.

### 9. Blocking and CPU work

Blocking work must not execute directly on the Worker event loop.

Blocking I/O uses a bounded thread executor. CPU-intensive work uses a bounded process executor or an external job system when configured.

Executor worker counts and submission queues are bounded. Queue admission has a Deadline. Already-running thread work may continue after request cancellation, but its result is discarded and the work remains tracked until completion.

### 10. Supervisor and Worker lifecycle

The Supervisor owns Worker process handles, readiness aggregation, signals, bounded restart policy, and final exit status.

Worker startup must complete before readiness is announced. Startup failure triggers reverse-order cleanup.

Unexpected Worker exit may trigger bounded restart with rate limiting and backoff. A crash loop exhausts the restart budget and marks the service unhealthy instead of restarting forever.

The semantic baseline must not depend on fork-only inherited mutable state.

### 11. Graceful shutdown

Runtime states are:

```text
STARTING → RUNNING → DRAINING → STOPPING → STOPPED
```

Shutdown proceeds in order:

1. mark the service not ready;
2. stop accepting new connections;
3. stop admitting new requests and background work;
4. drain active requests and response streams until the graceful Deadline;
5. cancel remaining request and operation Scopes;
6. stop application-owned background tasks;
7. close extensions and external resources in reverse startup order;
8. flush Runtime Records and telemetry within bounded budgets;
9. close listeners, transports, and executors;
10. exit Workers and aggregate Supervisor status;
11. terminate remaining processes after the hard-stop Deadline and record forced shutdown.

Shutdown is idempotent. A repeated signal may shorten the remaining grace period but must preserve best-effort cleanup reporting.

### 12. Context, records, and observability

Connection, request, operation, Deadline, cancellation reason, identity, and Runtime Record context are Scope-local.

Application singletons must not retain request-scoped objects after Scope completion.

Runtime Record and telemetry pipelines are bounded and expose queue depth, truncation, drop, failure, and flush-timeout information.

Required observability includes connection, request, task, executor, Worker, backpressure, admission, cancellation, shutdown, and Runtime Record metrics.

### 13. Required test classes

Implementation acceptance must cover:

- concurrent short connections and requests;
- keep-alive sequential behavior and attempted HTTP/1.1 pipelining;
- slow headers, bodies, readers, and streaming;
- client disconnect at multiple execution points;
- global, route, executor, and dependency saturation;
- bounded waiter queues;
- parent-to-child cancellation;
- Deadline budgets not resetting in nested calls;
- request-context isolation and detached-task context clearing;
- Worker startup rollback, crash, bounded restart, and crash-loop stop;
- graceful drain, grace expiry, hard-stop expiry, and repeated signals;
- no leaked tasks, connections, files, executors, or request contexts;
- repeatable race and deadlock stress diagnostics.

## Intentionally deferred

- minimum supported Python version;
- public names for Scope, Deadline, limiter, and cancellation APIs;
- exact numeric defaults;
- mandatory third-party event loop or parser;
- listener socket distribution strategy;
- HTTP/2 and HTTP/3 multiplexing;
- physical source, module, and distribution placement.

## Rejected alternatives

- one thread per request;
- unbounded fire-and-forget tasks;
- global mutable request context;
- unlimited executor queues;
- resetting the full timeout duration at every nested layer;
- concurrent HTTP/1.1 request execution on one connection in the initial runtime;
- infinite Worker restart loops;
- shutdown that merely stops the event loop without draining and cleanup;
- requiring a third-party event loop for correctness.

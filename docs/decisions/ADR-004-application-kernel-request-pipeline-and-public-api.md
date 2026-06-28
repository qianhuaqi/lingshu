# ADR-004: Application Kernel, request pipeline, and minimum public API

- Status: Accepted
- Date: 2026-06-28
- Parent architecture Issue: #25
- Decision Issue: #40 (completed)
- Implemented by: PR #41
- Effective merge commit: `bb78918dc2bc92dd49c34258e3707abd37274f12`
- Detailed model: `docs/architecture/APPLICATION_KERNEL_AND_REQUEST_PIPELINE.md`

## Context

LingShu required a fixed application and request-execution contract before implementation. Without it, parallel contributors could create incompatible lifecycle states, middleware ordering, route mutation behavior, handler return rules, exception paths, or response-commit semantics.

## Decision

### Public composition root and internal Kernel

The public application type is `LingShu`.

`LingShu` is the root composition facade. The low-level Application Kernel remains an internal `lingshu.core` mechanism and owns lifecycle state, registration catalogs, Application Revisions, freeze validation, immutable compiled-plan ownership, and resource-lifecycle contracts.

The Kernel does not own TCP listeners, protocol parsing, or business policy and must not import `lingshu.server`.

### Application lifecycle

```text
CREATED → CONFIGURING → FROZEN → STARTING → RUNNING
                                      ↓          ↓
                                   STOPPING ← DRAINING
                                      ↓
                                   STOPPED
```

- construction has no runtime side effects;
- registration is allowed only in `CREATED` and `CONFIGURING`;
- freeze validates and compiles one immutable Application Plan;
- freeze is idempotent for an unchanged revision;
- failed freeze publishes no partial plan;
- startup requires a frozen plan;
- running registries are immutable;
- draining stops new admission before shutdown cleanup;
- shutdown is idempotent and follows ADR-002.

### Application Revision and freeze

Configuration, routes, middleware, exception mappers, extensions, capabilities, and lifecycle hooks belong to an Application Revision.

Freeze validates configuration, route conflicts, handler and middleware signatures, exception mappings, extension dependencies, lifecycle ordering, and resource budgets. It then compiles immutable routing, middleware, exception, extension, capability, and lifecycle plans and publishes the complete plan atomically.

Direct mutation after freeze is rejected. Future reload must create a new revision and atomically switch validated plans; in-place mutation of a running plan is prohibited.

### Route contract

A route declaration contains a normalized path template, explicit methods, handler, optional name, route middleware, metadata, capability requirements, and later-approved body/response policies.

- registration order is not conflict resolution;
- duplicate and ambiguous routes fail at freeze;
- matcher specificity is explicit;
- 404 and 405 remain distinct;
- the running Router is immutable;
- automatic `HEAD`/`OPTIONS`, reverse routing, and mounts are deferred.

### Handler contract

Initial handlers are asynchronous and receive one explicit Request:

```python
async def handler(request: Request) -> Response | SupportedReturnValue:
    ...
```

Path parameters are accessed through Request. Core dependency injection and automatic synchronous-handler execution are not part of this decision. Handler signatures are validated before startup.

### Middleware contract

LingShu uses deterministic onion-style application and route middleware:

```python
async def middleware(request: Request, call_next: Next) -> Response:
    ...
```

- lower numeric priority enters earlier and exits later;
- equal priority uses explicit registration sequence within the revision;
- application middleware wraps route matching and the selected route pipeline;
- route middleware runs only after route match;
- egress is exact reverse order;
- middleware may short-circuit with a Response;
- `call_next` is single-use and Scope-bound;
- import order is not execution order.

Connection hooks, lifecycle hooks, and record sinks use separate contracts.

### Canonical request pipeline

```text
1. protocol request accepted by Server
2. create Request Scope and absolute Deadline
3. assign identities and open Runtime Record
4. create immutable request metadata and bounded body stream
5. perform Worker/Application admission
6. enter application middleware
7. route match
8. perform route admission and capability checks
9. enter route middleware
10. invoke asynchronous handler
11. normalize handler return to Response
12. unwind route middleware
13. unwind application middleware
14. resolve an unhandled exception when needed
15. finalize response metadata and body policy
16. commit response head
17. stream/write response with backpressure
18. finalize Runtime Record
19. cancel/await remaining request-owned tasks
20. release body, admission, context, and request resources
```

Every stage is observable and must preserve Deadline, cancellation, admission, cleanup, and Runtime Record rules.

### Request semantics

A Request belongs to one Request Scope and becomes invalid when that Scope completes.

- request metadata is read-only;
- route identity and path parameters become read-only after match;
- mutable application data uses explicit request-scoped state;
- extension state is namespaced or typed;
- body is bounded, backpressured, and single-consumer;
- buffering and decoding are explicit and limited;
- post-completion body or Request access fails;
- sensitive data is redacted from records by default.

### Handler return normalization

Every handler result is normalized exactly once.

Initially supported:

- `Response`;
- `str` as text under an explicit encoding/media policy;
- bytes-like data as binary;
- structured values only after a later serialization decision.

Rejected by default:

- `None` as implicit success;
- tuple response magic;
- arbitrary iterables as implicit streams;
- unknown objects.

Middleware returns Response, not unnormalized handler values.

### Response state and commit

```text
NEW → PREPARED → COMMITTED → COMPLETED
                  ↘          ↘
                   ABORTED ← ABORTED
```

- status, headers, cookies, and body policy are mutable only before `COMMITTED`;
- `PREPARED` is finalized but still replaceable;
- commit begins when the finalized response head is accepted by the Transport;
- only one response may be committed;
- pre-commit exceptions may replace the pending response;
- post-commit failures cannot create a second response and instead abort the stream/connection according to protocol policy;
- double commit, mutation after commit, and writes after completion are framework errors.

### Exception resolution

Resolution order:

1. most-specific route-scoped mapper;
2. most-specific application-scoped mapper;
3. built-in `HTTPException` mapping;
4. safe internal-error response before commit.

Mapper ambiguity fails at freeze. Mapper output is a Response. Mapper failure records both errors and falls back safely before commit. Sensitive details are hidden by default. Cancellation is not converted into an ordinary application error response. After commit, mapping cannot replace the response.

### Extension participation

Extensions may contribute schemas, capabilities, routes, middleware, exception mappers, lifecycle hooks, and approved record/telemetry sinks during configuration.

Freeze resolves dependencies and compiles contributions into the immutable plan. Startup follows dependency order; cleanup is reverse order. Extensions cannot mutate registries while running.

### Minimum public API

The root facade exposes:

```python
from lingshu import LingShu, Request, Response, HTTPException
```

Minimum usage shape:

```python
from lingshu import LingShu, Request, Response

app = LingShu()

@app.get("/")
async def index(request: Request) -> Response:
    return Response.text("hello")
```

Confirmed concepts include the `LingShu` facade, scoped Request, Response factories, intentional `HTTPException`, route decorators, middleware registration, exception-mapper registration, and extension registration.

Constructor details, server run/serve APIs, lifecycle decorator names, sync adaptation, dependency injection, automatic JSON/form/multipart behavior, and OpenAPI are deferred.

Root exports use explicit `__all__`. Kernel, plan, matcher, compiler, normalizer, commit-controller, and transport internals remain private unless separately promoted.

## Required acceptance tests

Implementation must test:

- legal and illegal Application state transitions;
- idempotent freeze and shutdown;
- no partial plan publication after freeze failure;
- mutation rejection after freeze;
- route conflict/ambiguity detection independent of registration order;
- deterministic middleware ingress, egress, priorities, and short-circuiting;
- double or delayed `call_next` rejection;
- immutable request metadata and scoped-state isolation;
- bounded single-consumer body behavior;
- handler signature and return-type validation;
- exactly-once normalization;
- pre-commit replacement and post-commit abort behavior;
- double-commit and mutation-after-commit rejection;
- exception mapper specificity and mapper-failure fallback;
- cancellation preservation;
- extension dependency/startup/reverse-cleanup behavior;
- no request, body, state, task, or response leakage;
- exact root export manifest and no import-time side effects.

## Rejected alternatives

- route, middleware, exception, or extension mutation while running;
- import-time registration;
- registration order as route conflict resolution;
- unordered middleware;
- multiple `call_next` calls;
- implicit sync-handler execution on the event loop;
- implicit tuple or `None` response magic;
- mutable Request metadata;
- multiple response commits;
- replacing a response after commit;
- exposing all deep implementation modules;
- per-request mutation of the compiled plan.

## Intentionally deferred

- configuration reload and multi-Worker plan rollout;
- complete exception taxonomy and client error schema;
- identifier formats;
- structured serialization and content negotiation;
- cookie, form, multipart, and upload APIs;
- automatic `HEAD` and `OPTIONS`;
- host routing, reverse routing, mounting, and sub-applications;
- public server run/serve and CLI semantics;
- synchronous handler adaptation;
- dependency injection;
- OpenAPI and official capabilities;
- exact numeric limits, timeouts, and media-type defaults.

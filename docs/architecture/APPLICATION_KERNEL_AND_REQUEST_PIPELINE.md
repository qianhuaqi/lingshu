# LingShu Application Kernel and Request Pipeline

- Status: Accepted through P0-D4
- Decision Issue: #40 (completed)
- Pull Request: #41
- Effective merge commit: `bb78918dc2bc92dd49c34258e3707abd37274f12`
- Parent Issue: #25
- Related ADR: `docs/decisions/ADR-004-application-kernel-request-pipeline-and-public-api.md`

## 1. Composition model

```text
Public LingShu facade
├─ internal Application Kernel
├─ immutable Application Plan
├─ HTTP application plan
├─ Runtime ownership plan
├─ Runtime Record protocols
├─ Extension plan
└─ Server delegation surface
```

The public facade assembles components. Lower components never import the facade. The internal Kernel owns lifecycle state, revisions, registration catalogs, freeze validation, immutable plans, and resource-lifecycle contracts. It does not own listeners or protocol parsing.

## 2. Application states

```text
CREATED
→ CONFIGURING
→ FROZEN
→ STARTING
→ RUNNING
→ DRAINING
→ STOPPING
→ STOPPED
```

- registration is allowed only before `FROZEN`;
- freeze is idempotent for an unchanged revision;
- freeze failure publishes no partial plan;
- startup requires a frozen plan;
- running registries are immutable;
- drain stops new admission;
- shutdown is bounded and idempotent.

## 3. Application Revision and Plan

A revision contains configuration, routes, application and route middleware, exception mappers, extensions, capabilities, lifecycle hooks, and resource-budget references.

Freeze validates and compiles conceptually:

```text
revision_id
validated_config
route_matcher
route_execution_plans
application_middleware_chain
exception_mapper_table
extension_lifecycle_plan
capability_plan
runtime_budget_plan
public_diagnostics
```

Publication is atomic. Future reload creates a new revision rather than mutating the running plan.

## 4. Route contract

A route contains:

```text
path_template
methods
handler
name?
route_middleware[]
metadata
required_capabilities[]
body_policy?
response_policy?
```

Rules:

- methods and templates are normalized;
- static/dynamic specificity is explicit;
- duplicate or ambiguous declarations fail at freeze;
- registration order never hides a conflict;
- 404 and 405 are distinct;
- compiled matching is immutable and concurrent-read safe;
- mounts, reverse routing, host routing, automatic HEAD, and automatic OPTIONS remain deferred.

## 5. Handler contract

```python
async def handler(request: Request) -> Response | SupportedReturnValue:
    ...
```

- exactly one explicit Request input initially;
- asynchronous callable required;
- route parameters are accessed through Request;
- no Core dependency injection;
- signatures are validated at freeze;
- child tasks remain request-owned unless explicitly transferred;
- sync-handler adaptation is deferred.

## 6. Middleware scopes and ordering

Application middleware wraps routing and the selected route pipeline. Route middleware runs only after a route match.

```python
async def middleware(request: Request, call_next: Next) -> Response:
    ...
```

Ordering:

```text
priority ascending
→ registration sequence ascending
```

Ingress follows that order; egress is exact reverse order.

`call_next` is single-use and Scope-bound. Middleware may short-circuit with a Response. Import order is not middleware order. Protocol, lifecycle, and record hooks use separate contracts.

## 7. Canonical request pipeline

```text
1. protocol acceptance
2. Request Scope and absolute Deadline
3. identities and Runtime Record
4. immutable Request and bounded body stream
5. Worker/Application admission
6. application middleware ingress
7. route match
8. route admission and capability checks
9. route middleware ingress
10. async handler
11. one-time return normalization
12. route middleware egress
13. application middleware egress
14. exception fallback when needed
15. response preparation
16. response-head commit
17. body/stream transmission with backpressure
18. Runtime Record finalization
19. cancel/await remaining request-owned tasks
20. release body, admission, context, and Scope resources
```

Each stage records outcome and preserves Deadline, cancellation, admission, and cleanup rules.

## 8. Request contract

Read-only metadata includes method, target, scheme, authority, path, query representation, protocol version, headers, connection metadata, and identities.

- route identity and path parameters appear after match and remain read-only;
- mutable application data uses request-scoped state;
- extension state is namespaced or typed;
- body is bounded, backpressured, and single-consumer;
- buffering/decoding is explicit and limited;
- access after Scope completion fails;
- Request is not a long-lived serializable business object;
- sensitive data is redacted by default.

## 9. Return normalization

Supported initially:

```text
Response
str
bytes-like
```

Structured values require a later serializer decision.

Rejected by default:

```text
None
tuple response magic
arbitrary iterator/generator
unknown object
```

Normalization happens exactly once. Middleware returns Response directly.

## 10. Response contract

```text
NEW → PREPARED → COMMITTED → COMPLETED
  ↘       ↘           ↘
   ABORTED ←────────── ABORTED
```

- NEW and PREPARED remain replaceable before commit;
- commit begins when the finalized response head is accepted by Transport;
- status and headers are immutable after commit;
- only one commit is allowed;
- pre-commit exception mapping may replace the pending response;
- post-commit failures abort the stream/connection and cannot produce a second response;
- writes after completion/abort fail;
- disconnect, cancellation, and application failure remain distinguishable.

## 11. Exception mapping

Resolution order:

1. most-specific route mapper;
2. most-specific application mapper;
3. built-in `HTTPException` mapping;
4. safe internal-error response before commit.

- equal ambiguity fails at freeze;
- mapper output is Response;
- mapper failure records both exceptions and falls back safely before commit;
- client-visible details are safe by default;
- cancellation is not converted into an ordinary error response;
- after commit, only abort/close and recording remain possible.

## 12. Extension integration

During configuration, extensions may contribute schemas, capabilities, routes, middleware, mappers, lifecycle hooks, and approved record/telemetry implementations.

Freeze resolves dependencies and compiles contributions. Startup is dependency order; shutdown is reverse order. During requests, extensions use compiled hooks, capabilities, and scoped state and may not mutate registries.

## 13. Minimum public facade

```python
from lingshu import LingShu, Request, Response, HTTPException
```

Example:

```python
from lingshu import LingShu, Request, Response

app = LingShu()

@app.get("/")
async def index(request: Request) -> Response:
    return Response.text("hello")
```

Confirmed public concepts:

- `LingShu` composition/registration facade;
- scoped immutable `Request`;
- `Response` construction/factories;
- intentional `HTTPException`;
- route method decorators;
- middleware registration;
- exception-mapper registration;
- extension registration.

Root exports are explicit through `__all__`. Kernel, plan, matcher, middleware compiler, normalizer, commit controller, parser, transport, and record-storage internals remain private.

## 14. Required tests

Implementation acceptance covers:

- all legal and illegal Application transitions;
- idempotent freeze and shutdown;
- no partial plan after failed freeze;
- mutation rejection after freeze;
- deterministic route conflict detection and matching;
- middleware priorities, reverse egress, short-circuit, and single-use `call_next`;
- Request immutability, scoped state, bounded body, and post-Scope access failure;
- handler signature and return validation;
- exactly-once normalization;
- Response transitions, one commit, pre-commit replacement, and post-commit abort;
- exception specificity, fallback, detail suppression, and cancellation behavior;
- extension dependency/startup/reverse-cleanup behavior;
- no task, body, Request, Response, or state leaks;
- exact public export manifest and no import-time I/O or task/process creation.

## 15. Deferred decisions

- full configuration reload and multi-Worker rollout;
- complete exception taxonomy and error-body schema;
- identifier formats;
- JSON and other serialization rules;
- cookies, form, multipart, uploads, and content negotiation;
- automatic HEAD and OPTIONS;
- host routing, reverse routing, mounts, and sub-applications;
- server run/serve and CLI APIs;
- sync handler adaptation;
- dependency injection;
- OpenAPI and official capabilities;
- exact media types, limits, and timeouts.

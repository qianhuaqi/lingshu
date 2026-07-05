# P4 Roadmap

Status: accepted by PR #102 / P4-00
Parent milestone: P3 developer-facing API ergonomics complete
P3 final Issue: #100
P3 final Pull Request: #101
P3 final merge commit: `b94da7c9f59cacf00a9ab497c14ffc4507a2661a`
P4-00 final Pull Request: #102
P4-00 merge commit: `f13a77892ea9e8960fd25aa4d51b554c51f36c84`

## 1. Why this document exists

P3 improved the developer-facing public surface. P4 must now prepare LingShu for official extensions without jumping directly into data stores or identity/access features.

This roadmap records the next safe sequence so contributors and agents do not add Redis, MySQL, MongoDB, identity/access, OpenAPI, multi-worker, reload/watch, adapters, public package publication, or production claims before the extension foundation exists.

## 2. P4 theme

P4 focuses on extension foundation work that still fits inside the current single-worker framework boundary.

The goal is to make later official extensions possible while preserving:

- zero mandatory runtime dependencies in the core package;
- native single-worker HTTP/1.1 scope;
- safe diagnostics and redaction behavior;
- deterministic request, response, scope, and cancellation contracts;
- one-Issue, one-branch, one-primary-writer governance.

## 3. Current baseline available to P4

P4 starts with:

- public root exports for `LingShu`, `Request`, `Response`, and `HTTPException`;
- route decorators for current HTTP method handling;
- immutable application freeze and lifecycle;
- request and response primitives;
- `Response.json(...)`;
- documented request-body ergonomics planning;
- safe error diagnostics policy;
- a future async-only `lingshu.testing.TestClient` decision;
- validated public-surface examples;
- native single-worker server;
- CLI `version`, `check`, and `run --workers 1`;
- clean packaging and CI evidence.

## 4. Proposed P4 sequence

```text
P4-00 P3 closeout and P4 roadmap
P4-01 async TestClient implementation
P4-02 extension contract and package boundary
P4-03 application resource lifecycle contract
P4-04 configuration redaction contract for extensions
P4-05 official extension packaging and dependency policy
```

### P4-00: P3 closeout and P4 roadmap

Update phase documents, record P3 closeout facts, and define the P4 task order. Do not change runtime code.

### P4-01: async TestClient implementation

Implement the narrow async `lingshu.testing.TestClient` accepted by P3-04. It should support in-process route dispatch, byte request bodies, response status/header/body capture, and focused tests. It must not replace real TCP integration tests.

### P4-02: extension contract and package boundary

Define how official extensions are named, imported, configured, and documented. Decide what lives in core versus optional extension packages. Do not add Redis, MySQL, MongoDB, or identity/access behavior yet.

### P4-03: application resource lifecycle contract

Define a safe pattern for application-owned resources to start, stop, and fail during lifecycle. This should cover ordering, cleanup, fatal scope, diagnostics, and testing, without binding to a specific external service.

### P4-04: configuration redaction contract for extensions

Define how optional extensions should accept configuration and keep sensitive values out of reprs, CLI diagnostics, and client-visible errors.

### P4-05: official extension packaging and dependency policy

Define package naming, optional dependency policy, compatibility expectations, and example boundaries for official extensions. This should prepare P5 data extensions without adding them in P4.

## 5. Deferred unless later authorized

The following remain deferred unless a later Issue and ADR explicitly authorize them:

- Redis extension implementation;
- MySQL extension implementation;
- MongoDB extension implementation;
- identity and access extension implementation;
- OpenAPI;
- multi-worker supervisor implementation;
- reload/watch;
- ASGI, WSGI, WebSocket, HTTP/2, or HTTP/3 adapters;
- new mandatory runtime dependencies in core;
- public package publication;
- production-readiness or performance claims.

## 6. Planned later sequence

After P4 completes, the expected next tracks are:

```text
P5 data extensions: Redis, MySQL, MongoDB
P6 identity and access extensions
```

P5 should start only after extension contract, resource lifecycle, configuration redaction, and packaging policy are accepted.

P6 should start only after P5 or a separate approved Issue confirms the application resource and extension foundation is stable enough for identity and access work.

## 7. First implementable P4 issue

After P4-00 merges, the first implementable Issue should be:

```text
P4-01: async TestClient implementation
```

P4-01 should stay narrow and implement only the public surface accepted by `docs/development/TEST_CLIENT_PLAN.md`.

## 8. Governance

Every P4 task must declare exact scope, dependency order, conflicts, required checks, and explicit exclusions.

Every P4 task still uses one Issue, one writer-prefixed branch, one primary writer, one isolated worktree or environment, and one Pull Request.

No direct commits to `main`, no auto-merge, no shared writable branch, and no consumer-before-provider merge.

## 9. P4-00 exit condition

P4-00 completed when:

- Issue #102 has a merged PR;
- stale phase and handoff documents no longer point to active P3 work;
- this roadmap is present on `main`;
- the project lead confirms P4-01 async TestClient implementation can proceed.

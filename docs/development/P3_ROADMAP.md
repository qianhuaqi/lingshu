# P3 Roadmap

Status: draft for Issue #90 / P3-00
Parent milestone: P2 hardening track complete
P2 final Issue: #88
P2 final Pull Request: #89
P2 final merge commit: `5dd74c2178121f52553d08cf3d8209094c1b8a69`

## 1. Why this document exists

P1 proved a minimum single-worker vertical slice. P2 audited and hardened the foundation. P3 must improve developer-facing ergonomics without expanding into integration or production tracks too early.

This roadmap records the next safe sequence so future contributors and agents do not jump directly to database integration, auth, multi-worker, reload/watch, OpenAPI, adapters, public package publication, or production claims.

## 2. P3 theme

P3 focuses on developer-facing API ergonomics that fit inside the current runtime boundary.

The goal is to make the existing framework easier to use and test while preserving:

- zero mandatory runtime dependencies unless a later Issue explicitly authorizes one;
- native single-worker HTTP/1.1 scope;
- safe diagnostics and redaction behavior;
- deterministic request, response, scope, and cancellation contracts;
- one-Issue, one-branch, one-primary-writer governance.

## 3. Current baseline available to P3

P3 starts with:

- public root exports for `LingShu`, `Request`, `Response`, and `HTTPException`;
- route decorators for current HTTP method handling;
- immutable application freeze and lifecycle;
- request and response primitives;
- native single-worker server;
- CLI `version`, `check`, and `run --workers 1`;
- static server configuration and safe CLI diagnostics;
- server operational hardening tests;
- developer ergonomics guide and future test-client planning document;
- clean packaging and CI evidence.

## 4. Proposed P3 sequence

```text
P3-00 phase transition and P3 roadmap
P3-01 JSON response ergonomics and content-type contract
P3-02 request body ergonomics and content negotiation planning
P3-03 error experience and safe diagnostics polish
P3-04 test client implementation decision
P3-05 examples for the accepted public surface
```

### P3-00: Phase transition and P3 roadmap

Update phase documents, record P1/P2 closeout facts, and define the P3 task order. Do not change runtime code.

### P3-01: JSON response ergonomics and content-type contract

Evaluate and implement a narrow JSON response path only if the Issue explicitly authorizes it. Define status, headers, charset, bytes serialization boundaries, and safe error behavior. Avoid broad validation or schema systems.

### P3-02: Request body ergonomics and content negotiation planning

Define how request body helpers and content-type handling should evolve. Do not introduce database, auth, OpenAPI, or validation frameworks.

### P3-03: Error experience and safe diagnostics polish

Improve developer-facing error messages while preserving redaction and client safety. Avoid tracebacks or secrets in client-visible diagnostics.

### P3-04: Test client implementation decision

Turn `docs/development/TEST_CLIENT_PLAN.md` into a concrete implementation decision. Decide whether the test client should live under `lingshu.testing`, how it should construct request scopes, and how it avoids diverging from the real server path.

### P3-05: Examples for the accepted public surface

Add or update examples only for APIs already accepted by earlier P3 Issues. Examples must be validated by tests or CLI checks and must not imply production readiness.

## 5. Deferred unless later authorized

The following remain deferred unless a later Issue and ADR explicitly authorize them:

- public package publication;
- production-readiness or performance claims;
- multi-worker supervisor implementation;
- reload/watch;
- runtime configuration hot reload;
- ASGI, WSGI, WebSocket, HTTP/2, or HTTP/3 adapters;
- dependency injection;
- OpenAPI;
- official database, cache, storage, auth, tenant, or RBAC integrations;
- new mandatory runtime dependencies;
- changes to frozen P0 decisions.

## 6. First implementable P3 issue

After P3-00 merges, the first implementable Issue should be:

```text
P3-01: JSON response ergonomics and content-type contract
```

P3-01 should stay narrow. It may only expand public API if the Issue defines exact API names, behavior, tests, docs, and compatibility expectations.

## 7. Governance

Every P3 task must declare exact scope, dependency order, conflicts, required checks, and explicit exclusions.

Every P3 task still uses one Issue, one writer-prefixed branch, one primary writer, one isolated worktree or environment, and one Pull Request.

No direct commits to `main`, no auto-merge, no shared writable branch, and no consumer-before-provider merge.

## 8. P3-00 exit condition

P3-00 completes when:

- Issue #90 has a merged PR;
- stale phase and handoff documents no longer point to active P2 work;
- this roadmap is present on `main`;
- the project lead confirms the first implementable P3 Issue can proceed.

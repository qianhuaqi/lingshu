# P2 Roadmap and LingShu 2.0 Direction

Status: draft for Issue #78 / P2-00
Parent milestone: P1 - Single-Worker Minimum Vertical Slice
P1 final Issue: #76
P1 final Pull Request: #77
P1 final merge commit: `dbb69a44fb186b9b82f763fb9a33fb76e5e1264f`
P1 acceptance evidence: `docs/development/P1_ACCEPTANCE_EVIDENCE.md`

## 1. Why this document exists

This document preserves the P2 plan and the LingShu 2.0 product direction inside the repository so future agents do not lose the reasoning from project discussions.

P1 proved a minimum vertical slice. P2 must not rush into feature expansion. P2 must first define the target, audit the foundation, lock the toolchain, and harden the single-worker runtime path.

## 2. LingShu 2.0 target

LingShu 2.0 is the long-term product target after the P1 minimum vertical slice.

LingShu 2.0 should become a reliable runtime foundation for AI-native business systems while preserving:

- strict architecture discipline;
- safe defaults;
- bounded resource ownership;
- clear request lifecycle;
- cancellation and deadline propagation;
- redacted diagnostics;
- verifiable Runtime Records;
- explicit extension and integration boundaries.

LingShu 2.0 is not authorized by P2 alone. It is a release gate that must be earned after production runtime, security model, documentation, integration boundaries, and compatibility policy are proven.

## 3. Problems LingShu 2.0 should solve

### 3.1 Safe framework foundation for AI-era applications

LingShu should make the request lifecycle predictable. Work should live inside explicit scopes. Deadlines and cancellation should flow through user code and framework-owned tasks. Framework imports should not create hidden global runtime state.

### 3.2 Operator-trustworthy production path

LingShu should eventually provide clear readiness, admission, shutdown, failure, and diagnostic behavior. Runtime Records should help explain what happened without leaking secrets. The project must not claim production readiness before this behavior is tested and documented.

### 3.3 Business-system integration boundary

Future database, cache, storage, and auth integrations must be explicit. The framework must not create import-time global connection pools. Request cancellation must release or roll back resources. Credentials, DSNs, tokens, tenant identifiers, and protected configuration must remain redacted.

### 3.4 Developer experience with governance

LingShu should provide clear CLI workflows, examples, stable errors, testing utilities, and documented extension points. Developer convenience must not bypass one-Issue, one-branch, one-PR governance.

### 3.5 Ecosystem growth without premature expansion

OpenAPI, dependency injection, auth, tenant, RBAC, database, cache, storage, WebSocket, ASGI, WSGI, multi-worker, reload/watch, and public package publication are future candidates. Each major capability needs an explicit Issue and usually an ADR before implementation.

## 4. P1 baseline available to P2

P2 starts from a merged P1 baseline with:

- installable root `lingshu/` package and clean wheel/sdist verification;
- zero mandatory runtime dependencies;
- public root exports for `LingShu`, `Request`, `Response`, and `HTTPException`;
- native single-worker HTTP/1.1 server and `serve()` entry point;
- CLI `version`, `check`, and `run --workers 1`;
- immutable application freeze and lifecycle;
- router, middleware, request, response, scope, deadline, safe error, redaction, and minimum Runtime Record behavior;
- examples and final acceptance evidence.

## 5. Corrected P2 sequence

```text
P2-00 governance docs and LingShu 2.0 roadmap
P2-01 framework audit baseline
P2-02 toolchain reproducibility
P2-03 static configuration hardening
P2-04 single-worker operational hardening
P2-05 developer ergonomics and examples
```

### P2-00: Governance documents and LingShu 2.0 roadmap

Refresh stale phase and handoff documents. Write the roadmap and 2.0 direction into the repository. Do not change runtime code.

### P2-01: Framework audit baseline

Produce `docs/development/P2_AUDIT_BASELINE.md`. Cover security, protocol safety, concurrency, database and storage boundaries, configuration, packaging, operations, and developer misuse risks.

### P2-02: Toolchain reproducibility

Pin or narrow development tool versions enough to avoid surprise format churn. Record the accepted Ruff formatting baseline and keep local commands aligned with CI.

### P2-03: Static configuration hardening

Strengthen startup configuration behavior, protected-value redaction evidence, CLI diagnostics, and documentation. Do not implement hot reload.

### P2-04: Single-worker operational hardening

Harden the existing single-worker server around malformed input, disconnects, drain, close, not-ready, admission, and bounded diagnostics. Do not implement multi-worker.

### P2-05: Developer ergonomics and examples

Improve examples, CLI workflows, failure-mode explanations, testing utilities, and contributor handoff. Do not add public APIs only for examples without a separate Issue.

## 6. Deferred unless later authorized

The following remain deferred unless a later Issue and ADR explicitly authorize them:

- public package publication;
- production-readiness or performance claims;
- multi-worker Supervisor implementation;
- reload/watch;
- runtime configuration hot reload;
- additional protocol or adapter expansion;
- dependency injection;
- OpenAPI;
- official database, cache, storage, auth, tenant, or RBAC integrations;
- new mandatory runtime dependencies;
- changes to frozen P0 decisions.

## 7. LingShu 2.0 release gate

LingShu must not claim 2.0 readiness until all of these are true:

- production runtime behavior is proven by tests and documentation;
- security and redaction model is reviewed;
- configuration and toolchain are reproducible;
- database and external-resource boundaries are explicit;
- compatibility policy exists;
- deployment guidance exists;
- CI and packaging evidence are stable;
- project lead explicitly authorizes the 2.0 milestone.

## 8. Governance

Every P2 task must declare exact base commit, primary writer, write scope, read dependencies, dependency order, conflicts, required checks, and explicit exclusions.

Every P2 task still uses one Issue, one writer-prefixed branch, one primary writer, one isolated worktree or environment, and one Pull Request.

No direct commits to `main`, no auto-merge, no shared writable branch, and no consumer-before-provider merge.

## 9. P2-00 exit condition

P2-00 completes when:

- Issue #78 has a merged PR;
- stale phase and handoff documents no longer point to P1-01 / PR #55;
- this roadmap is present on `main`;
- the project lead confirms the first implementable P2 Issue can proceed.

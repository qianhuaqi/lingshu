# P2 Roadmap

Status: draft for Issue #78 / P2-00
Parent milestone: P1 - Single-Worker Minimum Vertical Slice
P1 final PR: #77
P1 final Issue: #76
P1 final merge commit: `dbb69a44fb186b9b82f763fb9a33fb76e5e1264f`
P1 acceptance evidence: `docs/development/P1_ACCEPTANCE_EVIDENCE.md`

## Objective

P2 begins after the accepted P1 vertical slice. Its first job is to preserve the P1 closeout facts, refresh stale phase documents, and freeze an implementation order before new runtime work starts.

P2 should improve the existing single-worker development framework in a controlled order:

```text
phase closeout
→ configuration hardening
→ single-worker operational hardening
→ examples and developer documentation
→ later ADR-gated runtime expansion
```

## P1 baseline available to P2

P2 starts from a merged P1 baseline with:

- installable root `lingshu/` package and clean wheel/sdist verification;
- zero mandatory runtime dependencies;
- public root exports for `LingShu`, `Request`, `Response`, and `HTTPException`;
- native single-worker HTTP/1.1 server and `serve()` entry point;
- CLI `version`, `check`, and `run --workers 1`;
- immutable application freeze and lifecycle;
- router, middleware, request, response, scope, deadline, safe error, redaction, and minimum Runtime Record behavior;
- examples and final acceptance evidence.

## P2 non-goals unless later authorized

The following remain deferred unless a later Issue and ADR explicitly authorizes them:

- public package publication;
- production-readiness or performance claims;
- multi-worker Supervisor implementation;
- development reload/watch;
- runtime configuration hot reload;
- HTTP/2, HTTP/3, WebSocket, ASGI, or WSGI adapters;
- public streaming response API beyond internal bounded body primitives;
- form, multipart, file uploads, compression, or content encodings;
- automatic HEAD/OPTIONS;
- host routing, reverse routing, mounts, or sub-applications;
- sync Handler adaptation;
- dependency injection;
- OpenAPI;
- official Auth, Tenant, RBAC, SQL, Redis, Cache, Scheduler, Storage, or Observability integrations;
- new mandatory runtime dependencies;
- changes to frozen P0 decisions without a new Issue and ADR.

## Recommended Issue sequence

### P2-00: P1 closeout, phase state refresh, and P2 roadmap freeze

Documentation-only refresh.

Allowed scope:

```text
docs/development/CURRENT_PHASE.md
docs/development/HANDOFF.md
docs/development/P2_ROADMAP.md
README.md status section only if needed
CHANGELOG.md only if needed
```

No framework runtime code, tests, CI behavior, package metadata, or public API changes.

### P2-01: Static configuration hardening and CLI/config surface

Strengthen startup configuration behavior, protected-value redaction evidence, CLI diagnostics, and documentation.

Exclusions: no hot reload, no external config service, no new runtime dependency, and no production claim.

### P2-02: Single-worker server operational hardening

Improve evidence and behavior around the existing single-worker server surface: malformed input, disconnect, drain, close, not-ready, and bounded diagnostics.

Exclusions: no multi-worker, no reload/watch, no protocol rewrite, and no adapter expansion.

### P2-03: Developer ergonomics, examples, and docs

Improve documented examples, CLI workflows, failure-mode explanations, and contributor handoff.

Exclusions: no new public API just for examples and no framework behavior changes unless backed by a separate implementation Issue.

## Governance

Every P2 task must declare exact base commit, primary writer, write scope, read dependencies, dependency order, conflicts, required checks, and explicit exclusions.

Every P2 task still uses one Issue, one writer-prefixed branch, one primary writer, one isolated worktree/environment, and one Pull Request.

No direct commits to `main`, no auto-merge, no shared writable branch, and no consumer-before-provider merge.

## P2-00 exit condition

P2-00 completes when:

- Issue #78 has a merged PR;
- stale phase and handoff documents no longer point to P1-01 / PR #55;
- this roadmap is present on `main`;
- the project lead confirms the first implementable P2 Issue can be opened.

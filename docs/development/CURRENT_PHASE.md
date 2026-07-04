# Current Phase

Project: LingShu Framework
Canonical repository: `qianhuaqi/lingshu`
Current phase: P4 - Extension foundation planning
Completed milestone: P1 - Single-Worker Minimum Vertical Slice
Completed track: P2 - roadmap, audit, tooling, config, server operations, and developer ergonomics
Completed track: P3 - developer-facing API ergonomics
Completed final P1 Issue: #76
Completed final P1 Pull Request: #77
P1 final merge commit: `dbb69a44fb186b9b82f763fb9a33fb76e5e1264f`
P1 acceptance evidence: `docs/development/P1_ACCEPTANCE_EVIDENCE.md`
Completed final P2 Issue: #88
Completed final P2 Pull Request: #89
P2 final merge commit: `5dd74c2178121f52553d08cf3d8209094c1b8a69`
Completed final P3 Issue: #100
Completed final P3 Pull Request: #101
P3 final merge commit: `b94da7c9f59cacf00a9ab497c14ffc4507a2661a`
Active Issue: #102 - P3 closeout and P4 roadmap
Active branch: `human/dodo/p4-00-phase-transition`
Primary writer: project lead / 小顾
Status: P1, P2, and P3 are complete; P4 planning is being written before extension implementation starts.
Next dependent phase allowed: no P4 implementation task until P4-00 is merged and the project lead confirms the roadmap.

## P1 closeout facts

P1 completed when PR #77 merged and Issue #76 closed as completed.

P1 delivered the first installable and tested LingShu vertical slice:

- root `lingshu/` package and Hatchling packaging;
- immutable `LingShu` application plan and lifecycle;
- request, response, routing, middleware, and safe handler contracts;
- runtime scopes, deadlines, cancellation, admission, and minimum Runtime Record behavior;
- native single-worker HTTP/1.1 server;
- CLI `version`, `check`, and `run --workers 1`;
- examples, integration tests, clean packaging verification, and cross-platform CI.

## P2 closeout facts

P2 completed when PR #89 merged and Issue #88 closed as completed.

P2 delivered:

```text
P2-00 #78: phase state and P2 roadmap refresh
P2-01 #79: framework audit baseline
P2-02 #82: toolchain reproducibility and Ruff baseline
P2-03 #84: static configuration and protected diagnostics
P2-04 #86: single-worker server operations
P2-05 #88: developer ergonomics, examples, and test-client planning
```

## P3 closeout facts

P3 completed when PR #101 merged and Issue #100 closed as completed.

P3 delivered:

```text
P3-00 #90 / PR #91: phase transition and P3 roadmap
P3-01 #92 / PR #93: JSON response ergonomics and content-type contract
P3-02 #94 / PR #95: request body ergonomics and content negotiation planning
P3-03 #96 / PR #97: error experience and safe diagnostics policy
P3-04 #98 / PR #99: test client implementation decision
P3-05 #100 / PR #101: examples for the accepted public surface
```

The accepted P3 additions include:

- `Response.json(...)`;
- request-body examples that use the existing `request.body.read()` contract;
- a documented request-body ergonomics plan;
- a safe error diagnostics policy;
- a future async-only `lingshu.testing.TestClient` direction, with implementation deferred;
- validated examples for the accepted public surface.

## P4 planning goal

P4 should build the extension foundation before official Redis, MySQL, MongoDB, or identity/access work begins.

Candidate P4 sequence:

```text
P4-00 P3 closeout and P4 roadmap
P4-01 async TestClient implementation
P4-02 extension contract and package boundary
P4-03 application resource lifecycle contract
P4-04 configuration redaction contract for extensions
P4-05 official extension packaging and dependency policy
```

## Later deferred tracks

The following remain deferred until after P4 establishes the extension foundation:

```text
P5 data extensions: Redis, MySQL, MongoDB
P6 identity and access extensions
```

## Active P4-00 scope

P4-00 may update only planning and status documents:

```text
docs/development/CURRENT_PHASE.md
docs/development/HANDOFF.md
docs/development/P3_ROADMAP.md
docs/development/P4_ROADMAP.md
README.md status section only if needed
CHANGELOG.md only if needed
```

P4-00 must not change framework runtime behavior, public APIs, tests, package metadata, CI behavior, or dependency declarations.

## Dependency gate

The first P4 implementation task is blocked until P4-00 merges and the project lead confirms the roadmap.

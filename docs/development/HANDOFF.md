# Development Handoff

Updated at: 2026-07-04
Project: LingShu Framework
Phase: P4 - Extension foundation planning
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
Active Issue: #102
Active branch: `human/dodo/p4-00-phase-transition`
Primary writer: project lead / 小顾
Status: P4-00 documentation refresh and P4 roadmap writing in progress.

## Implemented through P1

P1 produced a narrow, tested, installable vertical slice of the framework:

- package, CI, DCO, type/lint/test/build governance, and clean-install artifact checks;
- core time helpers, identifiers, framework errors, safe Problem Details, and redaction primitives;
- immutable startup configuration snapshot;
- runtime deadlines, scopes, cancellation, task ownership, admission, bounded cleanup, and minimum Runtime Record behavior;
- HTTP value model, router, middleware, request, response, and handler contract safety;
- `LingShu` application kernel with route decorators, immutable freeze, lifecycle, and root facade exports;
- native single-worker HTTP/1.1 server;
- CLI `version`, `check`, and `run --workers 1`;
- integration, security, runtime watermark, packaging, example, and P1 acceptance evidence.

## Implemented through P2

P2 added the planning and hardening track:

1. P2-00: phase state refresh and P2 roadmap.
2. P2-01: framework audit baseline.
3. P2-02: toolchain reproducibility and Ruff formatting baseline.
4. P2-03: static configuration and protected diagnostics.
5. P2-04: single-worker server operational edges.
6. P2-05: developer ergonomics, example validation, and future test-client planning.

## Implemented through P3

P3 added the developer-facing ergonomics track:

1. P3-00: phase transition and P3 roadmap.
2. P3-01: `Response.json(...)` and JSON response contract.
3. P3-02: request body ergonomics planning.
4. P3-03: safe error diagnostics policy.
5. P3-04: future async-only test client decision.
6. P3-05: validated public-surface examples.

## Current task

P4-00 updates phase and handoff state, records P3 closeout, and writes the P4 roadmap.

P4-00 is documentation-only. It must not change framework runtime behavior, public APIs, CI behavior, packaging metadata, tests, or dependency declarations.

## Recommended P4 sequence

1. P4-00: P3 closeout and P4 roadmap.
2. P4-01: async TestClient implementation.
3. P4-02: extension contract and package boundary.
4. P4-03: application resource lifecycle contract.
5. P4-04: configuration redaction contract for extensions.
6. P4-05: official extension packaging and dependency policy.

## Later tracks

1. P5: Redis, MySQL, and MongoDB data extensions.
2. P6: identity and access extensions.

## Protected facts

- LingShu remains a pre-alpha single-worker framework baseline, not a production-ready stable release.
- Public package publication remains unauthorized.
- Redis, MySQL, MongoDB, identity/access, OpenAPI, multi-worker, reload/watch, and adapter tracks remain deferred until explicitly authorized by later Issues and ADRs.
- No direct commits to `main`.
- No auto-merge.
- Final merge authority belongs to the project lead.

## Next action

Open a Draft PR for Issue #102 from `human/dodo/p4-00-phase-transition`, verify documentation scope and CI, then wait for project-lead final merge review.

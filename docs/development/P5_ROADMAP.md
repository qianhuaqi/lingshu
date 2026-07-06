# P5 Roadmap

Status: active for P5-04 review
Context: Issue #124

## 1. Why this document exists

P5 starts after the P4 extension foundation is accepted. This roadmap now tracks
the shared `lingshu.db` foundation that later data extensions can consume
without making database clients mandatory core dependencies.

## 2. P4 closeout summary

P4 is closed. The accepted P4 contracts and final merge references are:

```text
P4-00 #102 / PR #102 / merge commit `f13a77892ea9e8960fd25aa4d51b554c51f36c84`: roadmap and phase closeout
P4-01 #104 / PR #105 / merge commit `f4753d39f6f710fea56c37f2f2851efb3e2ee186`: async TestClient and testing ergonomics
P4-02 #107 / PR #107 / merge commit `2998a3c42988ef8ccdb61bf54feb74ee5b7a72e9`: extension contract and package boundary
P4-03 #109 / PR #109 / merge commit `d55a34d3cdef19684b027eb840be7f57f61aedec`: application resource lifecycle contract
P4-04 #111 / PR #111 / merge commit `dcb069836d6860a2a03cb040caf98dcd95ec9ee5`: configuration redaction contract for extensions
P4-05 #113 / PR #113 / merge commit `65488f73383d043776ea48b0ab5a2c3cd201600b`: official extension packaging and dependency policy
```

The P4 contracts establish the extension boundary, lifecycle rules, redaction
rules, and packaging policy that later implementation work must follow.

## 3. P5 goals

- Establish an import-safe database foundation before backend-specific drivers.
- Keep the core package free of new mandatory runtime dependencies.
- Preserve the accepted P4 contracts as the baseline for any later implementation work.
- Keep diagnostics, reprs, logs, and handoff summaries free of secret leakage.
- Make the next implementation entry point explicit after cleanup.

## 4. P5 non-goals

- Implementing Redis, MySQL, MongoDB, ORM, query builders, migrations, or
  connection pooling.
- Implementing identity/access.
- Implementing OpenAPI.
- Implementing multi-worker mode.
- Implementing reload/watch.
- Implementing ASGI, WSGI, WebSocket, HTTP/2, or HTTP/3 adapters.
- Publishing a public package.
- Adding new core mandatory runtime dependencies.
- Making production-ready or performance claims.

## 5. P5 dependency baseline

P5 depends on the accepted P4 contracts:

- P4-02 extension contract and package boundary;
- P4-03 application resource lifecycle;
- P4-04 configuration redaction for extensions;
- P4-05 official extension packaging and dependency policy.

P5 implementation work must stay inside these boundaries and must not reopen
P4 runtime scope.

## 6. Suggested P5 order

Suggested sequence:

1. P5-00: P4 closeout and P5 data extensions roadmap.
2. P5-01: Redis data extension track.
3. P5-02: MySQL data extension track.
4. P5-03: repository cleanup and documentation synchronization before implementation.
5. P5-04: lingshu.db database layer foundation.

Suggested order rationale:

- Redis first as the simplest official data-extension baseline.
- MySQL second to validate SQL-oriented packaging and lifecycle patterns.
- Cleanup third to keep the repository state synchronized before new code.
- `lingshu.db` fourth to provide a shared database-layer contract before any
  backend-specific driver package.

## 7. Validation and CI expectations

- Keep the diff within the allowed documentation files.
- Run the merge-conflict marker grep before submit.
- Run `git diff --cached --stat` before submit.
- When Python 3.12+ dev dependencies are available locally, run `python -m ruff format --check .`, `python -m ruff check .`, `python -m mypy`, and `python -m pytest`.
- If Windows local dependency installation is blocked by `WinError 10013`, record the failure and rely on Draft PR plus GitHub CI for the final gate.

## 8. Next implementable issue

The next implementable issue after P5-04 should be a backend-specific driver
track that consumes `lingshu.db` without adding mandatory database dependencies
to core.

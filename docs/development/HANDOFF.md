# Development Handoff

Updated at: 2026-07-06
Project: LingShu Framework
Phase: P5 - Redis data extension track
Completed milestone: P1 - Single-Worker Minimum Vertical Slice
Completed track: P2 - roadmap, audit, tooling, config, server operations, and developer ergonomics
Completed track: P3 - developer-facing API ergonomics
Completed track: P4 - extension foundation planning
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
Completed final P4 Issue: #112
Completed final P4 Pull Request: #113
P4 final merge commit: `65488f73383d043776ea48b0ab5a2c3cd201600b`
Active Issue: #116 - P5-01: Redis data extension track
Active branch: human/dodo/p5-01-redis-data-extension
Primary writer: project lead / 小顾
Status: P5-01 is active; the Redis contract track is document-first and runtime-free.

## P4 closeout

P4 closeout references:

- P4-00 #102 / PR #102 / `f13a77892ea9e8960fd25aa4d51b554c51f36c84`
- P4-01 #104 / PR #105 / `f4753d39f6f710fea56c37f2f2851efb3e2ee186`
- P4-02 #107 / PR #107 / `2998a3c42988ef8ccdb61bf54feb74ee5b7a72e9`
- P4-03 #109 / PR #109 / `d55a34d3cdef19684b027eb840be7f57f61aedec`
- P4-04 #111 / PR #111 / `dcb069836d6860a2a03cb040caf98dcd95ec9ee5`
- P4-05 #113 / PR #113 / `65488f73383d043776ea48b0ab5a2c3cd201600b`

Accepted P4 contracts:

- extension contract and package boundary;
- application resource lifecycle contract;
- configuration redaction contract for extensions;
- official extension packaging and dependency policy.

## P5-01 scope

P5-01 records the Redis extension contract and keeps the track document-first.
It does not implement Redis, Redis Cluster, Redis Sentinel, identity/access,
OpenAPI, multi-worker, reload/watch, adapters, public package publication, or
production/performance claims.

## P5 roadmap

1. P5-00: P4 closeout and P5 data extensions roadmap.
2. P5-01: Redis data extension track.
3. P5-02: MySQL data extension track.
4. P5-03: MongoDB data extension track.

## Validation and CI

- Keep the diff within the allowed documentation files.
- Run the merge-conflict marker grep before submit.
- When local Python 3.12+ dependencies are available, run `ruff format --check`, `ruff check`, `mypy`, and `pytest`.
- If Windows local dependency installation is blocked by `WinError 10013`, record it and rely on Draft PR + GitHub CI for final verification.

## Next action

Continue with Redis contract design, then determine whether a minimal testable skeleton is actually needed.

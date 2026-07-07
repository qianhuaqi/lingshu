# Development Handoff

Updated at: 2026-07-06
Project: LingShu Framework
Phase: P5-06 Minimal MySQL data extension driver
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
Active Issue: #128 - P5-06: Minimal MySQL data extension driver
Active branch: human/dodo/p5-06-minimal-mysql-driver
Primary writer: project lead
Status: P5-06 is active; it adds the minimal optional MySQL integration boundary in
`lingshu.db.mysql` using existing `lingshu.db` contracts and application
lifecycle hooks.

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

## P5-06 scope

P5-06 introduces `lingshu.db.mysql` as the minimal optional MySQL boundary:

- `MySQLDriver` implementing `DatabaseDriver`;
- `make_mysql_resource(config, *, driver)` factory for `DatabaseResource`;
- `LingShu.add_database_resource()` integration remains inert at registration and
  startup/shutdown-bound at lifecycle;
- registration is not network-connected and startup is the first boundary where
  concrete acquisition may happen.

It does not implement ORM/ODM, query builder, migration, connection pooling,
untrusted plugin isolation, identity/access, OpenAPI, multi-worker, reload/watch,
HTTP adapters, or production performance claims.

## P5 roadmap

1. P5-00: P4 closeout and P5 data extensions roadmap.
2. P5-01: Redis data extension track.
3. P5-02: MySQL data extension track.
4. P5-03: repository cleanup and documentation synchronization before implementation.
5. P5-04: lingshu.db database layer foundation.
6. P5-05: Application lifecycle and app.db injection boundary.
7. P5-06: Minimal MySQL data extension driver.

## Validation and CI

- Keep the diff within the current issue write scope.
- Run merge-conflict marker checks before submit.
- Run `ruff check`, `mypy`, and `pytest`.
- If local dependency installation is blocked or baseline toolchain issues happen,
  record them and rely on Draft PR + GitHub CI for final verification.

## Next action

Finish remaining P5-06 validation, then prepare Draft PR summary for review.


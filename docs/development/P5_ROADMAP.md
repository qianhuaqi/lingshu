# P5 Roadmap

Status: active for P5-07 implementation
Context: Issue #130

## 1. Why this document exists

P5 started after the P4 extension foundation is accepted. This roadmap now tracks
the shared `lingshu.db` foundation and minimal backend drivers that can consume
it without making database clients mandatory dependencies of core.

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

- Keep core import-safe and free of mandatory database client dependencies.
- Keep `lingshu.db` shared contracts in place and only add optional backend
  boundaries.
- For MySQL, implement a minimal pool lifecycle boundary through
  `MySQLDriver.startup()` and `shutdown()`.
- Preserve redaction rules and non-sensitive `repr`/`safe_details` behavior.

## 4. P5 non-goals

- implementing full MySQL query APIs;
- implementing migration frameworks;
- implementing query builders or ORM;
- adding pool tuning options, health checks, reconnect/retry policy, or query
  routing.
- expanding startup/shutdown to acquire/release/query helpers or transaction APIs;
- implementing runtime-wide performance claims.

## 5. P5 dependency baseline

- P4-02 extension contract and package boundary;
- P4-03 application resource lifecycle;
- P4-04 configuration redaction for extensions;
- P4-05 official extension packaging and dependency policy.

P5 implementation work must stay inside these boundaries and must not reopen P4
runtime scope.

## 6. P5 sequencing

1. P5-00: P4 closeout and P5 data extensions roadmap
2. P5-01: Redis data extension track
3. P5-02: MySQL data extension track
4. P5-03: repository cleanup and documentation synchronization before implementation
5. P5-04: lingshu.db database layer foundation
6. P5-05: Application lifecycle and app.db injection boundary
7. P5-06: Minimal MySQL data extension driver
8. P5-07: Minimal MySQL connection pool lifecycle boundary

## 7. P5-07 implementation objective

Issue #130 adds:

1. `MySQLDriver` startup migration from `aiomysql.connect(...)` to
   `aiomysql.create_pool(...)`.
2. Opaque pool-handle lifecycle return from startup.
3. `shutdown()` still using `close()` + `await wait_closed()`.
4. `DatabaseConfigurationError` for missing `create_pool` callable
   (`db.mysql.pool_unavailable`).

## 8. Validation and CI expectations

- Keep diff within issue scope.
- Run merge-conflict marker grep before submit.
- Run `ruff check`, `mypy`, and `pytest`.
- If local environment has baseline toolchain issues, record and report clearly.

## 9. Next implementable issue

The next implementable track after P5-07 is the minimal Redis/MySQL optional
driver catalog sequencing defined in future backend issues.

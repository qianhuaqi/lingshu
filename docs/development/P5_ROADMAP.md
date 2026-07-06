# P5 Roadmap

Status: active for P5-06 implementation
Context: Issue #128

## 1. Why this document exists

P5 starts after the P4 extension foundation is accepted. This roadmap now tracks
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
- Introduce a minimal MySQL driver boundary that can be exercised through
  `LingShu.add_database_resource()`.
- Preserve redaction rules and non-sensitive `repr`/`safe_details` behavior.

## 4. P5 non-goals

- implementing full MySQL query APIs;
- implementing migration frameworks;
- implementing query builders or ORM;
- implementing connection pooling;
- implementing production-ready performance claims;
- implementing runtime-wide MySQL access policies beyond startup/shutdown boundary.

## 5. P5 dependency baseline

- P4-02 extension contract and package boundary;
- P4-03 application resource lifecycle;
- P4-04 configuration redaction for extensions;
- P4-05 official extension packaging and dependency policy.

P5 implementation work must stay inside these boundaries and must not reopen
P4 runtime scope.

## 6. Suggested P5 order

1. P5-00: P4 closeout and P5 data extensions roadmap
2. P5-01: Redis data extension track
3. P5-02: MySQL data extension track
4. P5-03: repository cleanup and documentation synchronization before implementation
5. P5-04: lingshu.db database layer foundation
6. P5-05: Application lifecycle and app.db injection boundary
7. P5-06: Minimal MySQL data extension driver

## 7. P5-06 implementation objective

This issue adds:

1. `lingshu.db.mysql`
2. `MySQLDriver` (minimal contract-based async startup/shutdown boundary)
3. `make_mysql_resource(...)` helper backed by `DatabaseResource`
4. focused tests for import safety, registration/lifecycle behavior, optional
   dependency handling, and startup failure propagation.

## 8. Validation and CI expectations

- Keep diff within issue scope.
- Run merge-conflict marker grep before submit.
- Run `ruff check`, `mypy`, and `pytest`.
- If local environment has baseline toolchain issues, record and report clearly.

## 9. Next implementable issue

The next implementable track after P5-06 is the minimal Redis/MySQL optional
extension extension catalog sequencing defined in future backend issues.


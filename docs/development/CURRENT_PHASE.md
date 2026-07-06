# Current Phase

Project: LingShu Framework
Canonical repository: `qianhuaqi/lingshu`
Current phase: P5-03 repository cleanup and documentation synchronization before implementation
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
P4 accepted contracts and merge references:

```text
P4-00 #102 / PR #102 / merge commit `f13a77892ea9e8960fd25aa4d51b554c51f36c84`: P4 roadmap and phase closeout
P4-01 #104 / PR #105 / merge commit `f4753d39f6f710fea56c37f2f2851efb3e2ee186`: async TestClient and testing ergonomics
P4-02 #107 / PR #107 / merge commit `2998a3c42988ef8ccdb61bf54feb74ee5b7a72e9`: extension contract and package boundary
P4-03 #109 / PR #109 / merge commit `d55a34d3cdef19684b027eb840be7f57f61aedec`: application resource lifecycle contract
P4-04 #111 / PR #111 / merge commit `dcb069836d6860a2a03cb040caf98dcd95ec9ee5`: configuration redaction contract for extensions
P4-05 #113 / PR #113 / merge commit `65488f73383d043776ea48b0ab5a2c3cd201600b`: official extension packaging and dependency policy
```

Active Issue: #122 - P5-03: repository cleanup and documentation synchronization before implementation
Active branch: human/dodo/p5-03-repository-cleanup-sync
Primary writer: project lead / 小顾
Status: P5-03 is active; the repository cleanup track is document-first and runtime-free.
Next dependent phase allowed: `lingshu.db` database layer architecture / minimal skeleton after cleanup sync merge and project-lead confirmation.

## P5-03 cleanup goal

P5-03 audits repository cleanup, synchronizes the current phase and handoff
documents, and records the next implementation entry point without changing any
runtime behavior.

## P4 closeout facts

P4 completed when PR #113 merged and Issue #112 closed as completed.

P4 delivered the extension foundation:

- extension contract and package boundary;
- application resource lifecycle contract;
- configuration redaction contract for extensions;
- official extension packaging and dependency policy.

## P5 roadmap goal

P5 should keep the repository entry points synchronized, preserve the accepted
architecture and governance records, and leave runtime implementation for later
issues.

## P5 sequencing

```text
P5-00 P4 closeout and P5 data extensions roadmap
P5-01 Redis data extension track
P5-02 MySQL data extension track
P5-03 repository cleanup and documentation synchronization before implementation
```

## Deferred until later authorization

```text
identity/access
OpenAPI
multi-worker
reload/watch
ASGI / WSGI / WebSocket / HTTP2 / HTTP3 adapters
public package publication
production-ready or performance claims
new mandatory runtime dependencies in core
```

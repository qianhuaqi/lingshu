# Current Phase

Project: LingShu Framework
Current phase: C2-R1 - Auth Entry Dedup and Legacy Convergence
Phase type: implementation
Current branch: qwen/phase-c2-r1-auth-legacy-convergence
Current writer: qwen
Current issue: #23
Status: in progress
Next phase allowed: no

## Accepted Baseline

- Phase A accepted and merged.
- Phase B accepted and merged through PR #8.
- Phase C0 accepted and merged through PR #11.
- Phase C1 accepted and merged through PR #13.
- Phase C2.1 accepted and merged through PR #16.
- Phase C2.2A accepted and merged through PR #18.
- Phase C2-R0 accepted and merged through PR #20.
- Phase C2-RC accepted and merged through PR #22 (merge commit: `4132e4b`).

## Base Commit

- Base commit: 4132e4bec85cc09fedeed55f930e6f8faac31986
- Previous phase: C2-RC merged by PR #22

## Test Baseline

- `tests/test_c2_auth.py`: 111 passed.
- `tests/test_c2_tenant.py`: 127 passed.
- Full suite: 526 passed, 1 skipped, 0 failed.
- `pip check`: no broken requirements.

## Phase C2-R1 Goal

Consolidate the dual-track authentication system into a single implementation
chain with a clear Legacy compatibility facade. This phase is NOT about adding
new auth capabilities — it is about convergence and controlled deprecation.

## Current Stage

- Audit Gate A: read-only dual-track authentication audit.
- Implementation Gate B: compat layer + legacy forwarding (blocked on Gate A
  approval by Xiao Gu).

## Frozen Phases

- R2, R3, R6, C2.2B, C3 remain frozen until R1 is accepted.

## CLI Exception (Issue #21 approved, carried forward)

- Baseline `ed3ff04` lacks `app/v1/language/` directory.
- `app/v1/language/.gitkeep` was added in C2-RC as a minimal placeholder.
- No runtime behavior change.

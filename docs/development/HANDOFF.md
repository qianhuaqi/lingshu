# Development Handoff

Updated at: 2026-06-28
Project: LingShu Framework
Canonical repository: `qianhuaqi/lingshu`
Phase: P0 - Architecture Decision Review and Blueprint Consolidation
Issue: #25
Baseline: `main` after PR #29 merge commit `0b5310f5e90dd321f9d5c571a89904dca949847c`
Status: awaiting project-lead architecture decisions

## Confirmed repository state

- The repository has been renamed from `qianhuaqi/sanic_framework` to `qianhuaqi/lingshu`.
- The old GitHub URL redirects to the canonical repository.
- PR #28 established the greenfield P0 baseline.
- PR #29 merged the complete governance hardening and controlled Blueprint entrypoint.
- The previous Sanic-based repository is archived at `archive/legacy-sanic-20260628`.
- Archive commit: `b869270e0ec7cbc324d17ef246e39d0873aab14f`.
- Production source, legacy tests, old scaffolds, and old dependency configuration are absent from active `main`.
- P0 remains unaccepted and P1 remains blocked.
- Issue #25 is the only active architecture Issue.

## Completed governance work

- `DEVELOPMENT_CONSTITUTION.md` is the active governance contract.
- `P0_DECISION_STATUS.md` separates confirmed, rejected, and candidate decisions.
- `LINGSHU_FRAMEWORK_BLUEPRINT.md` is the controlled P0-RC0 architecture entrypoint.
- The former detailed v0.6 proposal is preserved under `docs/architecture/candidates/`.
- Package, multi-distribution, `src/`, directory, extension, support, and release layouts are explicitly non-executable candidates.
- Legacy implementation Issues have been closed or marked historical.

## Remaining P0 work

- Review the candidate design chapter by chapter with the project lead.
- Decide the final repository and package layout.
- Decide whether any `src/` layout will be used.
- Decide Core, HTTP, Server, Record, CLI, and official-extension boundaries.
- Integrate accepted `P0_HARDENING_CHECKLIST.md` requirements into the single Blueprint.
- Decide supported Python and platform versions.
- Decide release and compatibility policy.
- Decide license, contribution, and vulnerability-reporting policy.
- Prepare P1 scope only after all required decisions are confirmed.

## Verification

The active repository contains architecture and governance documents only. No production source, package skeleton, runtime dependency, framework implementation, or publishing configuration is authorized.

Runtime tests are not applicable at this phase. P0 review focuses on internal consistency, decision status, security and lifecycle completeness, and absence of accidental implementation authorization.

## Known repository history noise

During an earlier audit, three temporary files were accidentally committed directly to `main` and immediately removed. No temporary file remains in the tree. The six corrective/no-op commits remain visible because shared history was not rewritten.

Affected commit sequence:

- `eb12c697` / `5c7e5f54`;
- `4c88089a` / `5550e75f`;
- `333b90b2` / `788e3bf2`.

No production or governance file remains changed by those temporary commits.

## Next action

Confirm the first unresolved architecture decision. Do not start P1.

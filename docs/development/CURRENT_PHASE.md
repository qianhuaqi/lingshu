# Current Phase

Project: LingShu Framework
Current phase: C2-P1 - Simplified Directory and Release Roadmap
Phase type: non-implementation research
Current branch: research/directory-release-roadmap
Current writer: human
Current issue: #26
Current PR: #27
Status: awaiting review
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
- Blueprint v0.7 freeze hardening is present on `main` at `b869270`.

## Phase Goal

Record the project lead's approved simplified package direction and define what
must be completed by every planned release through v1.0 before implementation
continues.

The target package root is `lingshu/`, not a permanent `src/lingshu/` layout.
The mandatory framework kernel is `lingshu/core/`, and official integrations are
owned by `lingshu/extensions/`.

## Scope

### In scope

- Record ADR-006 for the simplified package root and official extension model.
- Define the canonical target repository/package tree.
- Define core and official-extension ownership boundaries.
- Map reviewed C2-R1–R6 work into release versions.
- Define concrete release outcomes and exit gates from v0.7.x through v1.0.0.
- Record how and when the physical `src/lingshu/` to `lingshu/` move occurs.
- Identify later updates required for constitution, architecture contracts,
  packaging, scaffolds, tests, documentation, and repository tools.

### Out of scope

- Production source changes.
- Moving or deleting `src/lingshu/`.
- Changing `pyproject.toml` package discovery.
- Removing or renaming Stable public APIs.
- Implementing C2-R1 or any later refactor phase.
- Auto-merging PR #27.

## Deliverables

- `docs/decisions/ADR-006-simplified-package-root-and-official-extensions.md`
- `docs/architecture/target-directory-plan.md`
- `docs/roadmap/RELEASE_ROADMAP.md`
- Updated phase and handoff records.

## Review Focus

1. `core` must remain dependency-light and must not absorb optional integrations.
2. Official extensions must have explicit ownership and dependency direction.
3. Existing C2-R1–R6 analysis must be preserved and re-mapped, not discarded.
4. The physical removal of `src/` must be isolated from behavioral refactoring.
5. Every planned version must have concrete completion and exit criteria.

## Next Phase Condition

The next implementation phase may begin only after:

1. PR #27 is independently reviewed and accepted by Xiao Gu;
2. the project lead performs the final merge;
3. Issue #26 is closed as completed;
4. the next version/phase Issue is created from the merged release roadmap.
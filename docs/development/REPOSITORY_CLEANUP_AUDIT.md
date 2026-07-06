# Repository Cleanup Audit

Issue: #122
Branch: `human/dodo/p5-03-repository-cleanup-sync`
Scope: repository cleanup and documentation synchronization before implementation

## 1. Current valid document entrances

- [README.md](../../README.md): concise repository landing page and status summary.
- [Current phase](CURRENT_PHASE.md): active phase fact source.
- [Development handoff](HANDOFF.md): active handoff fact source.
- [P5 roadmap](P5_ROADMAP.md): current P5 ordering and phase state.
- [Framework blueprint](../architecture/LINGSHU_FRAMEWORK_BLUEPRINT.md): long-lived architecture source.
- [Accepted ADRs](../decisions): accepted architectural and governance decisions.
- [MySQL extension contract](MYSQL_EXTENSION_CONTRACT.md): retained contract draft for the earlier MySQL track.
- No top-level `legacy/` or `archive/` worktree directories are present in this
  checkout; historical archive material is referenced from docs only.

## 2. Expired but retained historical documents

- `docs/development/P1_IMPLEMENTATION_PLAN.md`
- `docs/development/P1_ACCEPTANCE_EVIDENCE.md`
- `docs/development/P2_AUDIT_BASELINE.md`
- `docs/development/P2_ROADMAP.md`
- `docs/development/P3_ROADMAP.md`
- `docs/development/P4_ROADMAP.md`
- `docs/development/REDIS_EXTENSION_CONTRACT.md`

These files remain useful as history and reference material, but they are not the
active source of truth for the current cleanup phase.

## 3. Documents with state mismatches

- `README.md` previously described P3 planning and broad developer setup content
  instead of the current P5-03 cleanup state.
- `docs/development/CURRENT_PHASE.md` previously described P5-00/P4 closeout
  state instead of the P5-03 cleanup phase.
- `docs/development/HANDOFF.md` previously described the P5-02 MySQL track
  instead of the current cleanup task.
- `docs/development/P5_ROADMAP.md` previously described the P5-02 review state
  and stale next-issue pointer.
- `docs/development/MYSQL_EXTENSION_CONTRACT.md` is still valid as a retained
  contract draft, but it is no longer the active phase description.

## 4. Suggested delete, archive, or merge candidates

- Merge repeated phase status snippets across `CURRENT_PHASE.md`,
  `HANDOFF.md`, and `P5_ROADMAP.md` into a smaller shared pattern in a later
  documentation pass.
- Keep the historical P1/P2/P3/P4 roadmap files as archives for now, but they
  can be consolidated into a single history index later if the team wants a
  shorter entry surface.
- Keep `MYSQL_EXTENSION_CONTRACT.md` for now; if the MySQL track is reworked
  again, its lifecycle should be handled in a dedicated follow-up issue.

## 5. Code redundancy and follow-up cleanup candidates

- The repository still contains several narrow support packages and boundary
  modules that should be reviewed later for overlap, especially around config
  handling, testing helpers, and extension scaffolding.
- Any candidate runtime cleanup must be handled in a separate issue so that this
  repository cleanup task stays documentation-first and does not change runtime
  behavior.
- Empty or compatibility-only package markers should be audited in a dedicated
  cleanup pass before deletion is considered.

## 6. README / CURRENT_PHASE / HANDOFF / P5_ROADMAP sync result

- README now states the current cleanup phase, the active issue, the active
  branch, and the next post-cleanup entry point.
- CURRENT_PHASE now treats P5-03 as the active phase and records the cleanup
  track as document-first and runtime-free.
- HANDOFF now matches the same P5-03 cleanup state and branch.
- P5_ROADMAP now points at the cleanup review state and the next post-cleanup
  implementation entry point.

## 7. Recommended next issue

After this cleanup lands, the next recommended implementation entry point is the
`lingshu.db` database layer architecture / minimal skeleton issue.

## 8. Notes

- No runtime files were changed for this audit.
- No dependencies were added.
- No legacy or archive content was deleted.

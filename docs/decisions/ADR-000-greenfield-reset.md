# ADR-000: Greenfield repository reset

- Status: Accepted direction; pending merge
- Date: 2026-06-28
- Issue: #25

## Context

The previous repository contains a Sanic-based implementation, legacy application scaffolding, tests, compatibility rules, and architecture documents. LingShu is now defined as a completely independent Python Web/API framework developed from scratch.

Continuing on the old working tree would repeatedly mislead human and AI developers into treating the legacy implementation as a migration baseline.

## Decision

1. Preserve the previous repository state in `archive/legacy-sanic-20260628`.
2. Establish a clean greenfield branch containing only architecture and governance facts.
3. Do not migrate, adapt, or preserve legacy Sanic code for compatibility.
4. Do not carry old API deprecation rules into the new framework before v1.0.
5. Treat the old branch as non-authoritative reference material only.
6. Begin production implementation only after P0 Blueprint acceptance and creation of a P1 Issue.

## Consequences

- The new branch has no production source code or old tests.
- Existing open legacy Issues must be closed or explicitly marked historical before P1.
- Any useful concept from the legacy repository must be re-approved under the new Blueprint before reimplementation.
- Repository history remains available through the archive branch and Git history, while the active working tree is clean.

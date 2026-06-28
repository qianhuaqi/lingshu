# Changelog

All notable user-visible changes to LingShu are documented in this file.

The format uses `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, and `Security`. Releases follow `docs/governance/RELEASE_AND_COMPATIBILITY_POLICY.md`.

## [Unreleased]

### Added

- Frozen P0 architecture through ADR-001 to ADR-007.
- Apache-2.0 license, NOTICE, DCO contribution process, contribution policy, security policy, code of conduct, compatibility/release policy, and P1 implementation plan.
- Initial P1 package foundation at version `0.1.0.dev0` using the root-level `lingshu/` layout and Hatchling.
- Component package boundaries and typed-package marker.
- Installed-version CLI reporting through `lingshu version` and `python -m lingshu --version`.
- Baseline package, import-safety, CLI, artifact-inventory, DCO, and cross-platform CI gates.
- Core wall/monotonic time contracts and strict RFC3339 UTC helpers.
- Typed opaque runtime identifiers and deterministic SHA-256 RevisionId.
- Stable framework error taxonomy, immutable safe details, and safe Problem Details mapping.

### Changed

- Project phase moved from P0 architecture/governance to P1 single-Worker implementation.
- `lingshu.core` changed from an empty package marker to the first explicit provider surface.

### Deprecated

- None.

### Removed

- None.

### Fixed

- Removed stale documentation that described the accepted governance and package layout as unresolved proposals.

### Security

- Hidden framework errors and unexpected exceptions now map to generic client-safe `internal.error` documents without serializing causes.

<!--
Release template:

## [X.Y.Z] - YYYY-MM-DD

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
-->

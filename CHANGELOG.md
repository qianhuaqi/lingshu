# Changelog

All notable user-visible changes to LingShu are documented in this file.

The format uses `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, and `Security`. Releases follow `docs/governance/RELEASE_AND_COMPATIBILITY_POLICY.md`.

## [Unreleased]

### Added

- Frozen P0 architecture through ADR-001 to ADR-007.
- Apache-2.0 license, NOTICE, DCO contribution process, contribution policy, security policy, code of conduct, compatibility/release policy, and P1 implementation plan.
- Initial P1 package foundation at version `0.1.0.dev0` using the root-level `lingshu/` layout and Hatchling.
- Empty component package boundaries and typed-package marker.
- Installed-version CLI reporting through `lingshu version` and `python -m lingshu --version`.
- Baseline tests for package metadata, import safety, CLI version reporting, artifact inventory, and DCO sign-offs.
- GitHub Actions matrix for quality, required Python/platform tests, preview Python, build, sdist rebuild, and clean installation.

### Changed

- Project phase moved from P0 architecture/governance to P1 single-Worker implementation.
- Repository agent and development-constitution rules now reference the frozen P1 authority.

### Deprecated

- None.

### Removed

- None.

### Fixed

- Removed stale documentation that described the accepted governance and package layout as unresolved proposals.

### Security

- No released vulnerability is recorded.

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

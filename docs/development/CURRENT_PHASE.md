# Current Phase

Project: LingShu Framework
Canonical repository: `qianhuaqi/lingshu`
Current phase: P1 - Single-Worker Minimum Vertical Slice
Active Issue: #52 — P1-00 package, tooling, CI, and governance foundation
Active Pull Request: #53
Active branch: `human/dodo/p1-00-package-tooling-ci`
Primary writer: qianhuaqi / 小顾
Base commit: `4c925c20e53b5c3fc6005c5c07f2b32d5175a0f5`
Planned version: `0.1.0.dev0`
Status: implementation complete; CI green; awaiting independent review and project-lead merge
Next dependent phase allowed: no

## P0 result

P0 is Frozen through ADR-001 to ADR-007. The PR #51 merge commit is the authoritative architecture baseline.

## P1-00 result under review

P1-00 establishes:

- root `pyproject.toml` using Hatchling and PEP 621;
- root-level `lingshu/` package with no `src/` directory;
- version `0.1.0.dev0` as the single manually maintained version;
- empty component package boundaries;
- installed-version CLI only;
- pytest, Ruff, and mypy development tooling;
- required Python/platform CI matrix and non-blocking Python 3.15 preview;
- wheel/sdist validation, sdist rebuild comparison, and clean non-editable install;
- DCO and governance checks;
- synchronized README, agent, constitution, phase, handoff, and changelog text.

## Verified evidence

GitHub Actions CI run #2 passed:

- Ruff lint and format check;
- mypy strict package check;
- pytest;
- DCO sign-off validation;
- Linux CPython 3.12, 3.13, and 3.14;
- Windows CPython 3.12 and 3.14;
- macOS CPython 3.12 and 3.14;
- Linux CPython 3.15 preview;
- wheel and sdist build;
- artifact metadata/inventory and Apache-2.0 license files;
- wheel rebuild from sdist with matching metadata/inventory;
- non-editable wheel install and CLI/import smoke tests outside checkout;
- uninstall verification.

## Explicit exclusions

P1-00 does not implement:

- `LingShu`, `Request`, `Response`, or `HTTPException`;
- core time, identifiers, errors, or configuration;
- Scope, Deadline, cancellation, tasks, or admission;
- HTTP messages, Router, Middleware, or Application Kernel;
- Runtime Record or Server behavior;
- CLI `check` or `run`;
- multi-Worker, reload, advanced protocol/body features, official integrations, or publication.

## Dependency gate

All later P1 Issues depend on P1-00. P1-01 must not begin until PR #53 is reviewed and merged by the project lead.

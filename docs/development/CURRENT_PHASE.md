# Current Phase

Project: LingShu Framework
Canonical repository: `qianhuaqi/lingshu`
Current phase: P1 - Single-Worker Minimum Vertical Slice
Active Issue: #52 — P1-00 package, tooling, CI, and governance foundation
Active branch: `human/dodo/p1-00-package-tooling-ci`
Primary writer: qianhuaqi / 小顾
Base commit: `4c925c20e53b5c3fc6005c5c07f2b32d5175a0f5`
Planned version: `0.1.0.dev0`
Status: implementation under review after Pull Request opens
Next dependent phase allowed: no

## P0 result

P0 is Frozen through ADR-001 to ADR-007. The PR #51 merge commit is the authoritative architecture baseline.

## Active objective

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

All later P1 Issues depend on P1-00. P1-01 must not begin until Issue #52's Pull Request is reviewed and merged by the project lead.

## Required evidence

- TOML parses and Python sources compile;
- Ruff, mypy, and pytest pass;
- build produces one `py3-none-any` wheel and one sdist;
- artifact inventory and license metadata pass;
- wheel rebuilt from sdist has matching metadata/inventory;
- non-editable wheel works outside checkout;
- imports have no process side effects;
- DCO check passes for all PR commits;
- no mandatory runtime dependency or `src/` directory exists.

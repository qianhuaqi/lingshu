# Current Phase

Project: LingShu Framework
Canonical repository: `qianhuaqi/lingshu`
Current phase: P1 - Single-Worker Minimum Vertical Slice
Completed foundation: P1-00 / Issue #52 / PR #53
Active Issue: #54 — P1-01 Core time, identifiers, errors, and safe Problem Details
Active Pull Request: #55
Active branch: `human/dodo/p1-01-core-foundations`
Primary writer: qianhuaqi / 小顾
Base commit: `689fb411f5d3ed03ad0059ede86bf532541e7249`
Verified implementation commit: `20a089683a6a35d3b8313489af6a0b32f7cc9691`
Planned version: `0.1.0.dev0`
Status: implementation complete; required CI green; awaiting independent review and project-lead merge
Next dependent phase allowed: no

## P1-01 result under review

P1-01 implements the first real `lingshu.core` provider surface:

- UTC wall-clock and process-local monotonic-clock contracts;
- strict RFC3339 UTC timestamps with trailing `Z`;
- typed opaque 128-bit runtime identifiers;
- deterministic SHA-256 RevisionId;
- bounded untrusted external request-correlation validation;
- LingShuError taxonomy, stable dotted codes, Severity, and FatalScope;
- immutable recursively validated safe details;
- client-safe `application/problem+json` Problem Details;
- generic `internal.error` mapping without cause, traceback, path, or secret leakage.

The root `lingshu` facade remains empty. The provider is exported only through `lingshu.core` until a later accepted facade task publishes root names.

## Verified evidence

GitHub Actions CI run #11 passed:

- Ruff lint and format check;
- mypy strict package check;
- full pytest suite and focused Core tests;
- DCO sign-off validation;
- Linux CPython 3.12, 3.13, and 3.14;
- Windows CPython 3.12 and 3.14;
- macOS CPython 3.12 and 3.14;
- Linux CPython 3.15 preview;
- wheel and sdist build;
- artifact inventory and license metadata;
- wheel rebuild from sdist;
- non-editable clean installation outside checkout;
- CLI/import smoke tests and uninstall verification.

The temporary Ruff diagnostic job used during failure investigation was removed. The final workflow is unchanged from `main`.

## Explicit exclusions

P1-01 does not implement configuration, Deadline, cancellation reason, Scope, task ownership, admission, HTTP Request/Response, HTTPException, Router, Middleware, Application Kernel, Runtime Record, Server, CLI run/check, telemetry exporters, serializer registry, or mandatory runtime dependencies.

## Dependency gate

P1-02 and P1-03 remain blocked until PR #55 is independently reviewed and merged by the project lead. Consumers must then synchronize from the P1-01 merge commit.

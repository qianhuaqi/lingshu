# Current Phase

Project: LingShu Framework
Canonical repository: `qianhuaqi/lingshu`
Current phase: P1 - Single-Worker Minimum Vertical Slice
Completed foundation: P1-00 / Issue #52 / PR #53
Active Issue: #54 — P1-01 Core time, identifiers, errors, and safe Problem Details
Active branch: `human/dodo/p1-01-core-foundations`
Primary writer: qianhuaqi / 小顾
Base commit: `689fb411f5d3ed03ad0059ede86bf532541e7249`
Planned version: `0.1.0.dev0`
Status: implementation ready for CI and review
Next dependent phase allowed: no

## Active objective

P1-01 implements the first real `lingshu.core` provider surface:

- UTC wall-clock and process-local monotonic-clock contracts;
- strict RFC3339 UTC timestamps with trailing `Z`;
- typed opaque 128-bit runtime identifiers;
- deterministic SHA-256 RevisionId;
- untrusted external request-correlation validation;
- LingShuError taxonomy, stable dotted codes, Severity, and FatalScope;
- immutable allowlisted safe details;
- client-safe `application/problem+json` Problem Details;
- generic `internal.error` mapping without cause or secret leakage.

## Explicit exclusions

P1-01 does not implement configuration, Deadline, cancellation reason, Scope, task ownership, admission, HTTP Request/Response, HTTPException, Router, Middleware, Application Kernel, Runtime Record, Server, CLI run/check, telemetry exporters, serializer registry, or mandatory runtime dependencies.

The root `lingshu` facade remains empty. Consumers import the provider through `lingshu.core` until a later accepted facade Issue publishes root names.

## Dependency gate

P1-02 and P1-03 remain blocked until Issue #54's Pull Request is reviewed and merged by the project lead. Later consumers must synchronize from the P1-01 merge commit.

## Required evidence

- Ruff lint and format check;
- mypy strict package check;
- full pytest suite;
- identifier uniqueness/canonical/type/failure tests;
- strict wall/monotonic time tests;
- safe-details immutability and unsafe-value rejection;
- safe Problem Details and generic internal mapping;
- cancellation/control-flow preservation;
- DCO, build, artifact inventory, clean install, Python/platform matrix.

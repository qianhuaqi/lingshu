# Toolchain Reproducibility

Status: P2-02 baseline
Issue: #82

## Purpose

LingShu uses a strict development process with multiple agents and isolated branches. A broad formatter or linter version range can create large unrelated diffs and hide real framework changes.

This document defines the accepted P2 toolchain policy and the Ruff formatting baseline.

## Supported Python versions

Runtime package metadata requires:

```text
CPython >=3.12
```

The local baseline should use CPython 3.12 unless a task explicitly needs a newer interpreter. CI may additionally exercise newer Python versions to detect compatibility problems.

Do not use Python 3.11 or older for local validation. The source may use syntax and typing assumptions that require Python 3.12+.

## Runtime dependency policy

LingShu currently has no mandatory runtime dependencies:

```toml
dependencies = []
```

Do not add runtime dependencies during tooling, documentation, audit, configuration, or server-hardening tasks unless a later Issue explicitly authorizes that change.

## Development dependency policy

Development tools are intentionally bounded to narrow minor-version ranges.

Current P2-02 policy:

```toml
[build-system]
requires = ["hatchling>=1.26,<1.27"]

[project.optional-dependencies]
dev = [
  "build>=1.2,<1.3",
  "mypy>=1.11,<1.12",
  "pytest>=8.3,<8.4",
  "ruff>=0.13,<0.14",
]
```

The goal is not to freeze LingShu forever. The goal is to make local and CI behavior reproducible enough that developers and agents do not accidentally reformat the repository while doing unrelated work.

## Ruff baseline

The accepted formatting baseline is the one that passes:

```bash
python -m ruff format --check .
```

with the bounded Ruff range declared in `pyproject.toml`.

The first attempted P2-02 range used Ruff `>=0.8,<0.9`. CI showed that this older formatter range does not match the current accepted repository formatting baseline. P2-02 therefore aligns the narrow Ruff range to `>=0.13,<0.14` instead of forcing a broad reformat of unrelated source files.

A Ruff upgrade must use a dedicated Issue and PR. It must not be mixed with feature work, server hardening, configuration changes, protocol work, or runtime refactoring.

A formatter upgrade PR must clearly state one of the following:

1. no formatting baseline changed; or
2. formatting baseline changed intentionally and all reformatting is isolated in that PR.

## Recommended clean local setup

Use a fresh virtual environment for validation:

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Required validation sequence

Run the same command forms that CI uses:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy lingshu
python -m pytest
python -m build
python tests/packaging/check_artifacts.py validate dist
git diff --check
```

Use `python -m ...` instead of bare console scripts when possible. This ensures commands resolve to the active virtual environment.

## Upgrade governance

Toolchain upgrades require:

- a dedicated Issue;
- a dedicated branch;
- a dedicated PR;
- no mixed feature work;
- explicit mention of whether formatting changed;
- CI green on the new baseline;
- project-lead final merge approval.

Do not broaden formatter ranges simply to chase the latest tool release.

## Non-goals

P2-02 does not authorize:

- runtime dependencies;
- framework runtime changes;
- protocol changes;
- database, cache, storage, auth, tenant, RBAC, or OpenAPI integration;
- multi-worker, reload/watch, ASGI, WSGI, WebSocket, HTTP/2, or HTTP/3 work;
- production-readiness claims;
- public package publication.

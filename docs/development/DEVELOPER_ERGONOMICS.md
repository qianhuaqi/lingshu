# Developer Ergonomics Guide

Status: P2-05 baseline
Issue: #88

## Purpose

This guide describes the current local development loop for LingShu. It documents the framework surface that exists today and avoids future-facing production claims.

LingShu is still a pre-alpha framework baseline. It is single-worker only and is not approved for public package publication or production use.

## Current supported loop

Use this loop for day-to-day work:

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m ruff check .
python -m ruff format --check .
python -m mypy lingshu
python -m pytest
```

Before opening or updating a PR, also run:

```bash
python -m build
python tests/packaging/check_artifacts.py validate dist
git diff --check
```

Prefer `python -m ...` commands so the active virtual environment is used consistently.

## CLI commands available today

### Validate an application

```bash
python -m lingshu check examples.hello_world:app
```

This validates the target import, application type, and frozen application contract without binding a socket.

### Run the native server

```bash
python -m lingshu run examples.hello_world:app --workers 1
```

Only one worker is supported. Passing any other worker count is a safe usage error. Multi-worker supervision is intentionally out of scope for the current P2 baseline.

## CLI exit codes

```text
0  success
2  usage error
3  target resolution error
4  application contract error
5  unsupported worker count
6  runtime failure
```

Diagnostics must remain safe: CLI errors should not print tracebacks, raw secrets, or unreviewed internal details.

## Example policy

Examples must:

- use only the currently supported public API;
- be small enough to read quickly;
- be checkable by the CLI;
- avoid production-readiness claims;
- avoid optional runtime dependencies unless a later Issue explicitly authorizes them.

`examples/hello_world.py` is the minimal baseline example. Broader examples should be added only when the corresponding framework behavior is already implemented and tested.

## Current non-goals

P2-05 does not add:

- production readiness;
- public package publication;
- JSON helper APIs;
- validation framework;
- dependency injection;
- OpenAPI;
- database, cache, storage, auth, tenant, or RBAC integration;
- multi-worker;
- reload/watch;
- ASGI, WSGI, WebSocket, HTTP/2, or HTTP/3 adapters;
- broad test-client implementation.

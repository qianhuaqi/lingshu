# Development Handoff

Updated at: 2026-06-28
Project: LingShu Framework
Canonical repository: `qianhuaqi/lingshu`
Phase: P0-D6 - Executable, CLI, Support Matrix, and Build Baseline
Parent Issue: #25
Active decision Issue: #46
Active decision branch: `human/dodo/phase-p0-d6-executable-build-baseline`
Baseline: latest accepted `main`
Status: proposed architecture ready for review

## Accepted decisions

- P0-D1: repository and concurrent-development governance through ADR-001 / PR #32.
- P0-D2: runtime concurrency through ADR-002 / PR #35.
- P0-D3: package and component layout through ADR-003 / PR #38.
- P0-D4: Application Kernel and request pipeline through ADR-004 / PR #41.
- P0-D5: Hardening Foundations through ADR-005 / PR #44.

## P0-D6 proposal completed on this branch

- Added `ADR-006-executable-cli-support-and-build-baseline.md`.
- Added `EXECUTABLE_AND_BUILD_BASELINE.md`.
- Defined ownership among Application, Server, Supervisor, and CLI.
- Proposed public single-Worker `lingshu.server` APIs: `Server`, `ServerConfig`, and `serve`.
- Proposed canonical console command `lingshu` and equivalent `python -m lingshu`.
- Proposed minimum commands `run`, `check`, and `version`.
- Defined strict `module:attribute` application discovery and explicit `--factory`.
- Rejected arbitrary expressions, file-path imports, implicit scanning, and factory call syntax.
- Defined production, development, and test profiles.
- Defined development reload as single-Worker child-process replacement.
- Defined cross-platform spawn semantics and per-Worker target import/freeze.
- Defined Supervisor-owned one-time listener bind and explicit Worker transfer.
- Defined RevisionId-consistent readiness, signal escalation, and stable exit codes.
- Proposed CPython >=3.12 with required 3.12/3.13/3.14 and 3.15 prerelease preview.
- Proposed Tier 1 64-bit Linux, Windows, and macOS.
- Chose Hatchling as the initial build backend.
- Chose static `[project].version` as the single version source.
- Defined console entry point, pure-Python wheel/sdist, clean-install, and CI gates.
- Added no production source, package skeleton, dependency, or workflow.

## Proposed public Server usage

```python
from lingshu.server import Server, ServerConfig, serve

server = Server(app, ServerConfig(host="127.0.0.1", port=8000))
await server.start()
await server.wait_closed()
```

Blocking single-Worker convenience:

```python
serve(app, host="127.0.0.1", port=8000)
```

The root facade remains:

```python
from lingshu import LingShu, Request, Response, HTTPException
```

## Proposed CLI

```text
lingshu run myapp.main:app
lingshu run myapp:create_app --factory
lingshu check myapp.main:app
lingshu version
python -m lingshu version
```

Target import is explicit and deterministic. Each spawned Worker imports and freezes its own Application and reports RevisionId/readiness.

## Proposed multi-Worker model

```text
CLI
└─ Supervisor
   ├─ bind listener once
   ├─ spawn Worker 1 → import/freeze/start
   ├─ spawn Worker 2 → import/freeze/start
   └─ report ready only when required Workers share one RevisionId
```

Correctness does not depend on fork inheritance or `SO_REUSEPORT`.

## Proposed support/build baseline

```text
CPython minimum: 3.12
Required:        3.12, 3.13, 3.14
Preview:         3.15 prerelease
Platforms:       Tier 1 64-bit Linux, Windows, macOS
Build backend:   Hatchling
Version source:  [project].version
Console script:  lingshu = "lingshu.cli:main"
Artifacts:       py3-none-any wheel + sdist
```

## Intentionally deferred

- actual implementation and files;
- actual first development version;
- License and public governance;
- numeric defaults and health endpoint paths;
- production SIGHUP/multi-Worker config coordination;
- advanced CLI and factory forms;
- PyPy, free-threaded, 32-bit, and native extensions;
- PyPI release, signatures, and attestations.

## Verification

Review must verify:

- Application does not become a process supervisor;
- Server remains single-Worker and Supervisor remains CLI/internal initially;
- target strings cannot execute arbitrary expressions;
- each Worker independently imports and freezes the same Revision;
- reload cannot be enabled with multiple Workers;
- listener bind and signal ownership are unambiguous;
- version is not duplicated;
- artifacts are tested outside checkout;
- P1 remains blocked.

## Next action

Review and merge the P0-D6 decision Pull Request only if the execution and build baseline is accepted. Do not create production files or begin P1.

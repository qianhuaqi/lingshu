# LingShu Executable and Build Baseline

- Status: Proposed for P0-D6
- Decision Issue: #46
- Parent Issue: #25
- Related ADR: `docs/decisions/ADR-006-executable-cli-support-and-build-baseline.md`

## 1. Purpose

This document turns P0-D6 into an implementation-ready contract without creating production files.

It defines:

- public single-Worker Server APIs;
- CLI command and target discovery behavior;
- multi-Worker Supervisor ownership;
- development reload boundaries;
- signal, readiness, and exit-code semantics;
- Python and platform support;
- build backend, version, metadata, artifacts, and CI gates.

## 2. Ownership map

```text
Application
  routes, middleware, extensions, configuration revision, lifecycle plan

Server
  one Worker runtime, one event loop, listeners/transports, protocol execution, drain

Supervisor
  processes, shared listener binding, Worker readiness, restart budget, signals, exit

CLI
  arguments, target specification, overrides, Supervisor setup, diagnostics, terminal exit
```

No layer bypasses accepted Kernel, Runtime, configuration, Record, or shutdown contracts.

## 3. Public `lingshu.server` surface

```python
from lingshu.server import Server, ServerConfig, serve
```

### `ServerConfig`

An immutable validated value object for one-Worker server configuration. It contains endpoint and bounded shutdown/runtime options after configuration merging.

### `Server`

Conceptual lifecycle:

```text
CREATED → STARTING → RUNNING → DRAINING → STOPPING → STOPPED
                         ↘                    ↑
                          FAILED ─────────────┘
```

Conceptual usage:

```python
server = Server(app, ServerConfig(host="127.0.0.1", port=8000))
await server.start()
await server.wait_closed()
```

Rules:

- one Worker and one event loop;
- `start()` freezes the Application before binding;
- failed freeze or startup performs bounded reverse cleanup;
- no process spawning;
- no global signal installation by default;
- close/drain is idempotent;
- startup cannot be repeated after terminal stop;
- readiness becomes true only after application/resources/record policy are ready.

### `serve`

```python
serve(app, host="127.0.0.1", port=8000)
```

Blocking convenience wrapper:

- owns the event loop;
- installs portable main-thread signals;
- blocks until clean or forced shutdown;
- rejects use from a running event loop;
- remains single-Worker;
- returns normally only for a clean shutdown and otherwise raises/maps an explicit startup/runtime failure.

## 4. CLI entry points

Equivalent launch forms:

```text
lingshu ...
python -m lingshu ...
```

Minimum commands:

### `lingshu run TARGET`

Starts one or more Workers and serves traffic.

### `lingshu check TARGET`

Imports the target, builds the Application Revision, validates configuration/extensions/routes/middleware, freezes it, and exits without opening a listener.

### `lingshu version`

Prints installed LingShu version, Python runtime, and platform support status. It does not import user application code.

## 5. Target grammar

```text
module:attribute
```

Accepted:

```text
project.api:app
project.api:create_app --factory
```

Rejected:

```text
app.py:app
project.api:create_app()
project.api:container.app
project.api:apps[0]
project.api:lambda
```

Validation:

- module consists of normal dotted identifiers;
- attribute is one identifier;
- no evaluation or implicit calls;
- no module scanning or fallback names;
- import and type errors are different outcomes;
- instance mode requires `LingShu`;
- factory mode requires synchronous zero-argument callable returning `LingShu`.

## 6. Target import and Worker isolation

For multi-Worker CLI execution:

```text
Supervisor
  parses target text and configuration sources
  binds listener
  spawns Workers

Each Worker
  imports module
  resolves instance/factory
  validates and freezes Application
  starts one event loop/runtime
  reports RevisionId + readiness
```

The Supervisor does not construct mutable Application state and then rely on process inheritance. Every Worker independently arrives at the same validated RevisionId.

## 7. Run command options

Baseline option contract:

```text
--factory
--host
--port
--workers
--config
--profile
--reload
--graceful-timeout
--hard-stop-timeout
--log-level
```

Rules:

- CLI values are higher precedence than file/environment sources and lower than explicit programmatic overrides only when such an embedding layer exists;
- values pass through the same schema validation as all other sources;
- unknown or contradictory options fail before binding;
- effective configuration can be displayed with source information under redaction rules;
- numeric defaults are deferred to tuning, not hidden inside CLI parsing.

## 8. Execution profiles

```text
production
development
test
```

- `run` defaults to production;
- `--reload` selects development;
- profile defaults remain schema-validated;
- development-only behavior never silently appears in production;
- test profile is used through controlled testing utilities and is not a production deployment profile.

## 9. Development reload

```text
watcher parent
└─ one child Worker
```

- only one Worker;
- process restart, not module reload;
- file changes debounced/coalesced;
- old child receives bounded graceful stop;
- replacement imports from a clean process;
- no zero-downtime production guarantee;
- excludes VCS, virtual environments, caches, build outputs, records, and configured paths;
- separate from revision-based production configuration reload.

`--reload --workers 2` or greater is a validation error.

## 10. Supervisor and process start

Cross-platform baseline:

```text
spawn
```

The semantic model is the same across Linux, Windows, and macOS.

Supervisor duties:

1. parse and validate CLI/options;
2. load non-application configuration sources;
3. bind listeners once;
4. spawn required Workers;
5. collect RevisionId/startup diagnostics;
6. wait for required readiness;
7. manage restart budget;
8. coordinate drain and hard stop;
9. return one stable exit code.

Deterministic import/configuration/freeze failures do not enter a restart loop.

## 11. Listener distribution

```text
Supervisor binds once
→ explicit socket handle/descriptor transfer
→ Workers accept from transferred listener
```

Properties:

- no independent port-bind race;
- no reliance on `SO_REUSEPORT` for correctness;
- port `0` resolves once;
- transfer mechanism is private and platform-specific;
- listener withdrawal is part of stop-admission;
- programmatic single-Worker Server binds directly.

## 12. Readiness model

Supervisor ready requires:

```text
listener bound
AND required Worker count alive
AND all Workers report same RevisionId
AND Application/extensions ready
AND Runtime Record required policy available
AND no fatal startup error
```

Not-ready states include startup, partial rollout, reload replacement, hard disk watermark, degraded configuration, and insufficient required Workers.

Liveness and readiness remain distinct.

## 13. Signal model

Portable expected behavior:

```text
first SIGINT/SIGTERM or Ctrl+C
→ graceful drain

second termination request
→ hard stop

graceful timeout
→ hard stop
```

- Supervisor owns process signals;
- programmatic Server installs signals only by explicit request in main thread;
- unsupported platform signals are not promised;
- SIGHUP configuration reload remains deferred;
- termination cause is recorded even when shell status varies by platform.

## 14. Exit codes

| Code | Meaning |
|---:|---|
| 0 | clean shutdown or successful check/version |
| 1 | uncategorized command failure |
| 2 | CLI usage/argument error |
| 3 | application import, discovery, or type error |
| 4 | configuration, validation, freeze, or extension-start failure |
| 5 | bind or platform startup failure |
| 6 | fatal Worker failure or restart budget exhausted |
| 7 | graceful shutdown timeout / forced hard stop |
| 8 | required Runtime Record policy unavailable |
| 70 | unexpected CLI/Supervisor internal defect |

Exit-code tests verify both code and safe diagnostic category.

## 15. Python support matrix

```text
Runtime implementation: CPython
Minimum version:        3.12
Required versions:      3.12, 3.13, 3.14
Preview version:        3.15 prerelease
requires-python:        >=3.12
```

No upper bound is encoded. Preview is visible but non-blocking until promoted after full gates.

Deferred:

- Python 3.11 and older;
- PyPy;
- free-threaded CPython;
- 32-bit builds;
- other interpreters.

## 16. Platform tiers

### Tier 1

Release blocking:

- maintained 64-bit Linux;
- supported 64-bit Windows desktop/server;
- supported 64-bit macOS.

Required architectures:

```text
Linux x86_64
Windows x86_64
macOS arm64
```

### Tier 2

When CI capacity exists:

```text
Linux arm64
macOS x86_64
```

Tier 2 status is explicit and cannot be advertised as Tier 1 without full release gates.

## 17. Build configuration

Build backend:

```toml
[build-system]
requires = ["hatchling>=1.26,<2"]
build-backend = "hatchling.build"
```

Rules:

- root-level `pyproject.toml` only;
- standard `[project]` metadata;
- no `setup.py` or `setup.cfg` initially;
- no dynamic metadata initially;
- build-backend change requires architecture review.

## 18. Project metadata baseline

Conceptual fields:

```toml
[project]
name = "lingshu"
version = "0.0.0"
requires-python = ">=3.12"
readme = "README.md"
```

`0.0.0` is illustrative only; P1/version planning chooses the actual development version.

License metadata is not populated until the license decision. Runtime dependencies begin empty unless approved by a dependency ADR.

## 19. Version source

Single manual source:

```text
[project].version in pyproject.toml
```

Runtime/CLI lookup:

```python
importlib.metadata.version("lingshu")
```

Prohibited:

- copied manual `__version__` string;
- separate component versions;
- tag/version mismatch;
- silent source-tree fallback in published runtime;
- SCM-derived dynamic version without a later decision.

## 20. Console script

```toml
[project.scripts]
lingshu = "lingshu.cli:main"
```

`main()`:

- parses arguments;
- returns integer status;
- does not import user code until a command requires it;
- does not start resources on module import;
- reaches `SystemExit` only at the outer executable boundary.

`lingshu/__main__.py` delegates to the same `main()`.

## 21. Artifact contract

Initial build outputs:

```text
lingshu-<version>-py3-none-any.whl
lingshu-<version>.tar.gz
```

Wheel includes approved package code/data only.

Excluded from wheel:

```text
tests/
docs source not declared as package data
tools/
benchmarks/
fuzz/
.git/
virtual environments
cache/build output
local config
Runtime Records
credentials/secrets
```

Sdist includes sufficient source and metadata to rebuild the wheel, README, and accepted governance/license files.

## 22. Packaging acceptance pipeline

```text
checkout
→ isolated wheel + sdist build
→ inventory/metadata inspection
→ clean venv
→ non-editable wheel install
→ change outside checkout
→ import + CLI + smoke tests
→ sdist rebuild
→ metadata/inventory comparison
→ editable-install developer test
→ clean uninstall verification
```

No repository `PYTHONPATH` injection is allowed. CI records artifact hashes.

## 23. CI matrix

Pull-request required matrix:

```text
Linux   3.12, 3.13, 3.14
Windows 3.12, 3.14
macOS   3.12, 3.14
```

Preview:

```text
Linux 3.15 prerelease — visible, non-blocking
```

Release candidate expands platform and packaging checks, including listener transfer and signal/shutdown behavior.

## 24. Required implementation tests

### Programmatic Server

- lifecycle and illegal transitions;
- freeze before bind;
- cleanup after failed startup;
- no implicit signals;
- `serve` loop/main-thread restrictions;
- idempotent drain/close.

### CLI and discovery

- command parity between script and `-m`;
- strict target grammar;
- no expression evaluation/scanning;
- instance/factory validation;
- distinct import/type/config diagnostics;
- stable exit codes.

### Processes and network

- spawn on Tier 1 platforms;
- import once per Worker;
- no mutable parent Application inheritance;
- one Supervisor bind;
- listener transfer;
- same RevisionId readiness;
- restart budget and deterministic startup-failure behavior;
- first/second termination and timeouts.

### Reload

- one Worker only;
- debounce and exclusion rules;
- child process replacement;
- no in-process stale module state.

### Build and compatibility

- Python version/implementation guard;
- Hatchling build;
- version metadata consistency;
- wheel/sdist inventory;
- clean install outside checkout;
- console entry points;
- no forbidden files;
- required CI matrix and visible preview.

## 25. Deferred decisions

- numeric defaults;
- health endpoint paths;
- SIGHUP and production multi-Worker config coordination;
- async/parameterized factories;
- advanced CLI commands;
- public multi-Worker Supervisor API;
- PyPy, free-threaded, 32-bit, and extra architectures;
- native extensions/platform wheels;
- exact OS version floors;
- license, release publication, signatures, and attestations.

## 26. Acceptance rule

Merging the P0-D6 decision PR accepts ADR-006 and this contract. It does not create the package or authorize P1. Production implementation begins only after the remaining P0 governance/freeze decision and explicit project-lead authorization.

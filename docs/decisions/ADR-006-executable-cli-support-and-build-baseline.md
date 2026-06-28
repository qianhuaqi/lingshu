# ADR-006: Executable entry points, CLI, support matrix, and build baseline

- Status: Proposed
- Date: 2026-06-28
- Parent architecture Issue: #25
- Decision Issue: #46

## Context

LingShu has accepted its runtime, package layout, Application Kernel, request pipeline, and hardening foundations. Before P1 creates the package skeleton, the project must decide how users start an application, how the CLI discovers application objects, how multi-Worker process ownership works, which Python/platform combinations are supported, and how artifacts are built and verified.

Without this decision, implementation could accidentally mix Application and Server ownership, rely on fork-only behavior, add unsafe import expressions, confuse development reload with configuration reload, duplicate version strings, or create incompatible packaging metadata.

## Decision

### 1. Execution ownership

The responsibility boundary is:

```text
LingShu Application
  owns routes, middleware, extensions, configuration revision, and application lifecycle

Server
  owns one Worker event loop, listeners/transports, protocol execution, signals delegated by caller, readiness, drain, and connection shutdown

Supervisor
  owns process creation, listener binding, Worker readiness aggregation, restart budget, process signals, and final exit code

CLI
  owns argument parsing, target discovery specification, configuration overrides, Supervisor construction, diagnostics, and terminal exit
```

The Application does not bind sockets or create Worker processes. The internal Kernel does not import Server. CLI and the documented Server facade compose accepted lower-level contracts.

### 2. Public single-Worker Server API

`lingshu.server` becomes a documented public subpackage with:

```python
from lingshu.server import Server, ServerConfig, serve
```

Conceptual API:

```python
config = ServerConfig(host="127.0.0.1", port=8000)
server = Server(app, config)
await server.start()
await server.wait_closed()
```

And a blocking helper:

```python
serve(app, host="127.0.0.1", port=8000)
```

Rules:

- `Server` is single-Worker only;
- `ServerConfig` is immutable and validated before binding;
- `start()` freezes an unfrozen Application before creating runtime resources;
- freeze failure creates no listener or partial Server state;
- programmatic `Server` does not install process-global signal handlers unless explicitly requested through a documented option;
- `serve()` owns the event loop, installs supported main-thread signal handlers, blocks until shutdown, and cannot be called from an already running event loop;
- repeated close/drain requests are idempotent;
- multi-Worker Supervisor remains internal to CLI in the initial public API;
- embedding APIs beyond this single-Worker surface are deferred.

The root package remains limited to `LingShu`, `Request`, `Response`, and `HTTPException`; Server APIs live in the documented `lingshu.server` subpackage.

### 3. Canonical CLI

Installation provides:

```text
lingshu
```

`python -m lingshu` is behaviorally equivalent.

Initial commands:

```text
lingshu run TARGET
lingshu check TARGET
lingshu version
```

`run` starts the service. `check` imports, validates, freezes, and reports diagnostics without binding a listener or starting business traffic. `version` prints the installed distribution version and supported runtime information without importing user application code.

Commands such as routes, shell, generate, migrate, and plugin management are deferred.

### 4. Application target grammar

The accepted target grammar is:

```text
module:attribute
```

Examples:

```text
myapp.main:app
myapp:create_app --factory
```

Rules:

- module is a normal dotted Python module name;
- attribute is one Python identifier, not an arbitrary expression or dotted traversal;
- file-path targets such as `app.py:app` are not accepted initially;
- parentheses, indexing, calls, lambdas, and evaluation expressions are prohibited;
- CLI does not scan modules to guess an application;
- the module must be importable in the active environment;
- target import failure and target type mismatch use distinct diagnostics and exit codes;
- without `--factory`, the attribute must be a `LingShu` instance;
- with `--factory`, the attribute must be a synchronous zero-argument callable returning a `LingShu` instance;
- async factories, parameter injection, and implicit environment arguments are deferred;
- user module import occurs once in each Worker process and must not be relied upon as a Supervisor-side singleton.

### 5. Run command baseline

Conceptual command:

```text
lingshu run myapp.main:app \
  --host 127.0.0.1 \
  --port 8000 \
  --workers 1
```

Initial options include:

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

Exact default numeric values are implementation tuning and remain deferred. Every effective value is reported with its source under safe diagnostic rules.

CLI overrides follow ADR-005 precedence and do not mutate the source configuration object.

### 6. Profiles

Initial profiles are:

```text
production
development
test
```

Rules:

- `run` defaults to production profile;
- development must be explicit through `--profile development` or `--reload`;
- `--reload` implies development profile;
- unsafe development behavior is never enabled by ambient environment alone without a declared source;
- profile selects validated defaults/policies but does not bypass schema validation;
- test profile is for controlled test harnesses and is not a production listener mode.

Exact profile values are deferred to P1 configuration implementation.

### 7. Development reload

Development reload is process restart, not in-process module reload and not ADR-005 configuration hot reload.

Rules:

- reload is single-Worker only;
- `--reload` with `--workers > 1` fails before startup;
- a lightweight parent watcher starts and restarts one child Worker process;
- change events are debounced and coalesced;
- the old child is drained/stopped within bounded time before replacement becomes authoritative;
- import caches and application state are reset by process replacement;
- `.git`, virtual environments, caches, build output, Runtime Record storage, and configured excluded paths are ignored;
- reload is a development convenience with no zero-downtime or production durability guarantee;
- production configuration revision reload remains a separate mechanism from ADR-005.

### 8. Multi-Worker process model

CLI multi-Worker execution uses an internal Supervisor and cross-platform spawn semantics.

Rules:

- `spawn` is the semantic baseline on Linux, Windows, and macOS;
- correctness never depends on inheriting a pre-imported mutable Application through `fork`;
- Supervisor parses CLI/configuration and validates target syntax but does not treat a parent-imported Application instance as Worker state;
- each Worker imports the target, creates/fetches the Application, validates/freeze it, starts one event loop, and reports its RevisionId and readiness;
- all required Workers must report the same RevisionId before the Supervisor reports ready;
- deterministic import/configuration/freeze failures are startup failures, not restart-loop candidates;
- unexpected runtime Worker exits follow ADR-002 restart budgets;
- Worker count must be a positive bounded integer;
- dynamic autoscaling is deferred.

### 9. Listener ownership

The Supervisor binds each configured listening socket once before Workers accept traffic.

- binding failure occurs before readiness and has a stable exit code;
- the bound socket is explicitly transferred/duplicated to spawned Workers through a platform-supported mechanism;
- correctness does not depend on `SO_REUSEPORT`;
- ephemeral port selection occurs once at Supervisor bind time;
- Workers do not independently race to bind the same endpoint;
- the Supervisor stops admission by closing/withdrawing listener ownership during shutdown;
- exact descriptor/handle transfer implementation is private and platform-specific.

Single-Worker programmatic `Server` binds its own listener because no Supervisor exists.

### 10. Readiness

Supervisor readiness requires:

- listener successfully bound;
- configured required Worker count started;
- every required Worker imported and froze the same Application Revision;
- required extensions/resources ready;
- Runtime Record required policy available;
- no startup fatal condition.

The process is not ready during startup, development child replacement, partial Worker rollout, hard disk watermark, or unresolved degraded configuration.

Liveness only means the Supervisor/Worker control loop is functioning; it does not imply readiness.

The concrete health endpoint is deferred.

### 11. Signals and shutdown

CLI/Supervisor owns process-level signal handling.

- first graceful termination signal enters DRAINING and begins ADR-002 shutdown;
- a second termination signal requests immediate hard stop;
- graceful timeout expiration escalates to hard stop;
- Unix SIGTERM and SIGINT are supported;
- interactive Windows Ctrl+C is supported; additional Windows control events are best-effort according to platform capability;
- unsupported signals are not advertised as portable behavior;
- SIGHUP configuration reload is deferred;
- programmatic `Server` only installs signal handling when explicitly requested and run in the main thread.

### 12. Exit-code contract

CLI uses stable process exit codes:

```text
0   clean requested shutdown / successful check or version
1   uncategorized command failure
2   CLI usage or argument error
3   application import/discovery/type error
4   configuration, validation, freeze, or extension-startup error
5   listener bind or platform startup error
6   runtime Worker fatal failure or restart-budget exhaustion
7   graceful shutdown timeout / forced hard stop
8   Runtime Record required-policy startup failure
70  unexpected internal CLI/Supervisor defect
```

Signals may produce platform-specific shell status externally, but LingShu diagnostics record the internal termination reason.

### 13. Python support

Initial support is:

```text
Implementation: CPython
Minimum:        Python 3.12
Required:       Python 3.12, 3.13, 3.14
Preview:        Python 3.15 prerelease until final validation
```

`requires-python` is:

```text
>=3.12
```

There is no artificial upper bound. A newly released Python minor becomes required only after passing the full compatibility gate. Preview failure is visible but non-blocking until promoted.

Initially unsupported/deferred:

- Python 3.11 and older;
- PyPy and other implementations;
- 32-bit Python;
- free-threaded CPython builds;
- embedded/minimal Python distributions without required standard-library behavior.

### 14. Platform support tiers

Tier 1, release blocking:

```text
64-bit Linux on a maintained mainstream distribution
64-bit Windows on a supported Microsoft desktop/server release
64-bit macOS on a supported Apple release
```

Required architecture coverage:

- Linux x86_64;
- Windows x86_64;
- macOS arm64;
- macOS x86_64 and Linux arm64 are Tier 2 when CI capacity is available.

Tier 1 failures block release. Tier 2 failures are documented and must not be silently presented as supported. Exact OS version floors are maintained in release metadata/tests rather than hard-coded forever in this ADR.

### 15. Build backend

LingShu uses Hatchling as its initial PEP 517 build backend.

Conceptual configuration:

```toml
[build-system]
requires = ["hatchling>=1.26,<2"]
build-backend = "hatchling.build"
```

Reasons:

- pure-Python package baseline;
- direct PEP 517/621 support;
- no `setup.py` execution model;
- explicit artifact selection;
- sufficiently small packaging surface.

Changing build backend requires a dedicated Issue/ADR because it affects release reproducibility and package inventory.

`setup.py` and `setup.cfg` are not created initially.

### 16. Project metadata

The root `pyproject.toml` uses standard `[project]` metadata.

Confirmed fields/concepts:

```text
name = "lingshu"
requires-python = ">=3.12"
readme = "README.md"
dynamic metadata: none initially
console script: lingshu
```

License metadata remains blocked until the governance/license decision. Placeholder or misleading license declarations are prohibited.

Runtime dependencies are empty initially unless a later dependency ADR approves one. Test, lint, type-check, build, and documentation tools are development dependencies and must not leak into mandatory runtime dependencies.

Optional feature dependencies use coherent extras only after the corresponding capability is accepted.

### 17. Authoritative version source

The sole manually edited version is static `[project].version` in `pyproject.toml`.

Rules:

- no duplicate manually maintained `__version__` literal;
- runtime and CLI read the installed distribution version using `importlib.metadata.version("lingshu")`;
- source checkout without installed metadata may use an explicit development fallback only in repository tooling, never silently in published runtime behavior;
- Git tags and release artifacts must match the project version;
- component-specific versions remain prohibited;
- migration to SCM-derived dynamic versioning requires a later ADR.

### 18. Console entry point

Conceptual metadata:

```toml
[project.scripts]
lingshu = "lingshu.cli:main"
```

`lingshu.cli:main` returns an integer exit code and does not call `os._exit`. The generated console script or `python -m lingshu` passes that code through `SystemExit` at the outer boundary.

Importing `lingshu.cli` must not import user application modules or start runtime resources.

### 19. Artifact policy

Initial releases build:

```text
one pure-Python wheel: py3-none-any
one source distribution
```

The wheel includes only approved `lingshu` package files and declared package data. It excludes tests, tools, benchmarks, fuzz corpora, caches, local configuration, Runtime Records, credentials, and development artifacts.

The sdist includes the source needed to rebuild the same wheel plus required license/governance files once accepted, README, and build metadata.

Native extensions or platform wheels require a later ADR.

### 20. Packaging verification

Every packaging-sensitive PR/release must:

1. build wheel and sdist in isolated mode;
2. inspect metadata and file inventory;
3. create fresh virtual environments;
4. install the wheel non-editably;
5. run imports, `lingshu version`, `python -m lingshu version`, and smoke tests outside the checkout;
6. rebuild a wheel from the sdist and compare expected metadata/inventory;
7. verify no repository `PYTHONPATH` is present;
8. verify unapproved files and secrets are absent;
9. test editable installation separately for developer experience;
10. uninstall and verify package-owned files are removed cleanly.

Artifact hashes are recorded by CI. Reproducible byte-for-byte builds are a target where tool/environment controls permit, but semantic metadata/inventory equality is the minimum initial gate.

### 21. CI compatibility matrix

Required pull-request matrix:

```text
Linux:   CPython 3.12, 3.13, 3.14
Windows: CPython 3.12 and 3.14
macOS:   CPython 3.12 and 3.14
```

Preview matrix:

```text
Linux: CPython 3.15 prerelease, non-blocking until promoted
```

Required checks include unit, contract, concurrency, protocol, security, packaging, import-boundary, and clean-install tests according to changed scope.

Release candidates run the expanded full matrix, artifact install tests, signal/shutdown tests, and platform-specific listener transfer tests.

A supported Python/platform combination cannot be removed without an Issue, migration notice, and release-policy review.

### 22. Required acceptance tests

Implementation must test:

- `Server` legal/illegal state transitions and idempotent close;
- `serve()` event-loop ownership and main-thread signal restrictions;
- `run`, `check`, `version`, and `python -m lingshu` parity;
- target grammar rejection of expressions, files, traversal, calls, and implicit scanning;
- instance/factory discovery and type validation;
- target import once per Worker and no parent Application state inheritance;
- spawn behavior on Tier 1 platforms;
- single Supervisor bind and explicit listener transfer;
- same RevisionId across ready Workers;
- startup failure, restart budget, first/second signal, graceful timeout, and hard-stop exit codes;
- reload single-Worker restriction and process replacement;
- Python version guard and unsupported implementation diagnostics;
- Hatchling wheel/sdist metadata and inventory;
- static version consistency with installed metadata and release tag;
- clean non-editable install outside checkout;
- absence of tests, tools, secrets, caches, and Runtime Records from wheel;
- CI matrix and preview failure visibility.

## Rejected alternatives

- Application object directly owning process supervision;
- Kernel importing Server;
- multi-Worker programmatic API in the initial root facade;
- fork-only correctness or inherited mutable Application state;
- each Worker racing to bind the same port;
- `SO_REUSEPORT` as correctness baseline;
- arbitrary Python expression evaluation in application targets;
- implicit module scanning or app guessing;
- in-process development module reload;
- multi-Worker development reload;
- Python 3.11 or older as initial minimum;
- an initial artificial Python upper bound;
- PyPy/free-threaded/32-bit support claims without gates;
- `setup.py` or `setup.cfg` as initial build configuration;
- duplicated version literals;
- dynamic versioning without a separate decision;
- publishing tests, tools, records, credentials, or caches in the wheel;
- treating editable installation as release evidence.

## Intentionally deferred

- exact numeric defaults for host, port, Workers, and timeouts;
- concrete health endpoint paths;
- SIGHUP reload and multi-Worker configuration rollout transport;
- advanced CLI commands;
- async or parameterized factories;
- public multi-Worker Supervisor API;
- PyPy, free-threaded builds, 32-bit platforms, and additional architectures;
- native extensions and platform wheels;
- exact OS version floors;
- License and public governance;
- PyPI publication and release signing/attestation policy.

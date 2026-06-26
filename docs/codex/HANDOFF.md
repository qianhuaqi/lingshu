# Development Handoff

Updated at: 2026-06-26
Location: office
Branch: codex/phase-c1-request-runtime
Worktree: clean
Work commit: 1b2aa0ee0c1f73d2700fe6d4053094beee025a5d

## Completed

- Implemented C1 request execution context with request id, trace id hook, optional operation id, compiled route policy, absolute monotonic deadline, cancellation reason, lifecycle state, ContextVar binding and explicit reset/detach paths.
- Implemented deadline helpers: `current_deadline()`, `remaining_time()`, `cancel()`, and `raise_if_cancelled()`.
- Implemented RoutePolicy definition, compiled immutable policy, registry and compiler skeleton with global to blueprint to route precedence and legacy RoutePolicy compatibility.
- Implemented managed `TaskRegistry` with owner-required spawn, strong references, list, cancel, cancel_all, shutdown_and_wait, completion cleanup and exception consumption.
- Implemented lifecycle state machine, `/live`, `/ready`, basic `/health`, drain rejection for business routes and `ShutdownCoordinator` with reverse cleanup, errors and idempotency.
- Added deterministic C1 contract tests for execution context isolation, policy precedence, managed tasks and lifecycle/drain/shutdown behavior.
- Updated governance files from Phase B to Phase C1 boundaries and added packaging assertion that the old unused internal manifest JSON is absent from wheels.

## Remaining

- Wait for Xiao Gu independent Phase C1 acceptance.

## Last verification

- editable install: passed with `.venv\Scripts\python.exe -m pip install -e ".[dev]"`
- pytest: 145 passed, 0 failed, 1 skipped
- contract check: Project check passed
- build: successfully built wheel and sdist
- diff check: passed
- wheel content smoke: passed for built-in languages, internal registry manifest, scaffold, no unused internal manifest JSON and no `framework` package
- wheel install smoke: passed for `import lingshu`, failed `import framework`, `lingshu --help`, and absent `sanic-framework`
- generated project smoke: passed with generated `c1_smoke` app `/health` returning 200 after disabling DB extensions through environment flags

## Known risks

- GitHub has no CI configured; evidence is from local Windows verification and temporary-venv smoke checks.
- Scaffold bootstrap still imports extension modules broadly; generated-project smoke disables DB extensions through environment flags to avoid external services.
- Sanic ASGI test client triggers server stop listeners between requests, so extension teardown remains listener-based while full shutdown coordination is explicit through `ShutdownCoordinator`.

## Next exact action

- Wait for Xiao Gu's Phase C1 review on PR #13.

## Current PR

- PR: #13
- Latest instruction: start Phase C1 from Issue #12; implement request execution foundation only, do not start Phase C2 or later.

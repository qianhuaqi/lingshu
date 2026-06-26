# Development Handoff

Updated at: 2026-06-26
Location: office
Branch: codex/phase-c1-request-runtime
Worktree: clean
Work commit: f8bdf564fbc851c5184202b31b35cc95a7150dc7

## Completed

- Implemented C1 request execution context with request id, trace id hook, optional operation id, compiled route policy, absolute monotonic deadline, cancellation reason, lifecycle state, ContextVar binding and explicit reset/detach paths.
- Implemented deadline helpers: `current_deadline()`, `remaining_time()`, `cancel()`, and `raise_if_cancelled()`.
- Implemented RoutePolicy definition, compiled immutable policy, registry and compiler skeleton with global to blueprint to route precedence and legacy RoutePolicy compatibility.
- Implemented managed `TaskRegistry` with owner-required spawn, strong references, list, cancel, cancel_all, shutdown_and_wait, completion cleanup and exception consumption.
- Implemented lifecycle state machine, `/live`, `/ready`, basic `/health`, drain rejection for business routes and `ShutdownCoordinator` with reverse cleanup, errors and idempotency.
- Added deterministic C1 contract tests for execution context isolation, policy precedence, managed tasks and lifecycle/drain/shutdown behavior.
- Updated governance files from Phase B to Phase C1 boundaries and added packaging assertion that the old unused internal manifest JSON is absent from wheels.
- Addressed Xiao Gu first review blockers for PR #13: `create_app()` stays `starting`, readiness is marked only after successful startup, startup failure stays non-ready and business routes return 503.
- Connected `ShutdownCoordinator` to Sanic stop listeners with one monotonic total deadline, in-flight request waiting, task-registry shutdown policy handling, reverse cleanup, concurrent caller sharing and stopped final state.
- Added `InFlightRequestTracker` and request finalization cleanup for normal, exception, timeout and cancellation paths.
- Hardened `TaskRegistry` scopes so `application` and `operation` tasks run in a cleaned context, request tasks are finished at request end, history is bounded, large results are not retained and `forget()` releases records.
- Enforced compiled RoutePolicy fail-closed behavior, duplicate or empty route-name rejection, explicit health route public policies and immutable compiled policies.
- Enforced request deadline execution at the handler boundary with stable LingShu timeout envelope and request context reset.
- Added PR #13 review regression coverage for lifecycle readiness, shutdown budgets, in-flight tracking, task context isolation, task retention, route-policy fail-closed behavior, request deadlines and multi-app isolation.

## Remaining

- Wait for Xiao Gu independent Phase C1 second-round acceptance.

## Last verification

- editable install: passed with `.venv\Scripts\python.exe -m pip install -e ".[dev]"`
- pytest: 158 passed, 0 failed, 1 skipped
- contract check: Project check passed
- build: successfully built wheel and sdist
- diff check: passed
- wheel content smoke: passed for built-in languages, internal registry manifest, scaffold, no unused internal manifest JSON and no `framework` package
- wheel install smoke: passed for `import lingshu`, failed `import framework`, `lingshu --help`, and absent `sanic-framework`
- generated project smoke: passed with generated app import and `/health` returning 200
- health endpoint smoke: passed for `/live`, `/ready` and `/health` returning 200
- timeout smoke: passed for route timeout returning HTTP 504 with LingShu code 990002 and handler `finally` running
- shutdown/drain smoke: passed with coordinator reaching `stopped` and `unfinished_requests=0`
- review boundary scans: production `asyncio.create_task` is limited to `src/lingshu/system/tasks.py`; app/scaffold code has no `lingshu.system` import; C2 keyword hits are limited to documented boundaries, existing legacy modules and tests

## Known risks

- GitHub has no CI configured; evidence is from local Windows verification and temporary-venv smoke checks.
- Scaffold bootstrap still imports extension modules broadly; generated-project smoke disables DB extensions through environment flags to avoid external services.
- Sanic ASGI test client triggers server stop listeners between requests; lifecycle restart support was added for tests, while production readiness remains startup-driven.
- C1 intentionally does not implement JWT, authorization, tenant resolution, HMAC, rate limiting, idempotency, ORM/Redis/Mongo redesign, OpenAPI, complete DI, events or C2 behavior.

## Next exact action

- Push this handoff update, post a PR #13 `[HANDOFF]` comment, then wait for Xiao Gu's second-round Phase C1 review.

## Current PR

- PR: #13
- Latest instruction: fix PR #13 first-round review blockers only; do not start Phase C2 or later.

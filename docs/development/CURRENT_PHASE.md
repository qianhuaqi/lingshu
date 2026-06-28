# Current Phase

Project: LingShu Framework
Canonical repository: `qianhuaqi/lingshu`
Current phase: P0 - Architecture Decision Review and Blueprint Consolidation
Phase type: non-implementation architecture and governance
Accepted baseline: latest accepted `main`
Active decision branch: none
Active decision Issue: none
Parent architecture Issue: #25
Status: P0-D2 accepted; awaiting next architecture decision
Next phase allowed: no

## Foundational fact

LingShu is a completely new, independently implemented Python Web/API framework.

It does not depend on Sanic, FastAPI, Flask, Django, Starlette, or any other upper-level Web framework. The archived implementation creates no compatibility obligation.

## Completed decisions

### P0-D1: Single repository and development concurrency

Accepted through ADR-001 and PR #32.

Confirmed:

- one canonical repository: `qianhuaqi/lingshu`;
- independent Issue, branch, primary writer, worktree or clone, virtual environment, and Pull Request per concurrent task;
- declared write scopes and integration order;
- parallel development with serial integration into `main`.

### P0-D2: Runtime concurrency

Accepted through ADR-002 and PR #35 at merge commit `6809a18b0284d18fd1ee46d9af7183521a66d67c`.

Confirmed:

- standard-library `asyncio` semantics as the correctness baseline;
- one event loop and one Application Runtime per Worker process;
- Supervisor-managed Workers with bounded restart and crash-loop stop;
- explicit Supervisor → Worker → Application → Connection → Request → Operation ownership;
- request-owned tasks by default and explicitly registered long-lived background tasks;
- no unregistered fire-and-forget tasks;
- one active request at a time per HTTP/1.1 connection, with concurrency across connections;
- bounded hierarchical admission, queues, executors, telemetry, and Runtime Record pipelines;
- end-to-end backpressure;
- absolute monotonic Deadline propagation;
- explicit cancellation reasons and parent-to-child propagation;
- bounded thread/process isolation for blocking and CPU-heavy work;
- ordered graceful shutdown with hard-stop escalation;
- context isolation, observability, leak gates, and concurrency stress tests.

## Still unresolved

- one distribution versus multiple distributions inside the single repository;
- `packages/` versus another repository layout;
- direct `lingshu/` versus `src/`;
- exact Core, HTTP, Server, Record, CLI, testing, and extension boundaries;
- Runtime Record default installation and physical placement;
- official built-in versus optional capabilities;
- Python and platform support range;
- public API names and numeric runtime defaults;
- listener distribution and HTTP/2/HTTP/3 semantics;
- release, compatibility, license, contribution, and security policies.

## Recommended next decision

P0-D3 should decide packaging, source layout, and component boundaries:

1. one distribution or multiple distributions;
2. direct `lingshu/` or `src/lingshu/`;
3. one or multiple `pyproject.toml` files;
4. Core, HTTP, Server, Record, CLI, Testing, and Extensions physical boundaries;
5. public imports and dependency direction;
6. test, benchmark, fuzz, example, and tooling directory placement.

## Out of scope

- production framework implementation;
- source package or directory skeleton creation;
- runtime dependency introduction;
- package publication;
- starting P1.

P1 remains blocked until all P0 exit conditions are satisfied and the project lead explicitly authorizes it.

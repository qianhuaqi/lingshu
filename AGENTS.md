# Repository Agent Rules

## Highest-priority project fact

LingShu is a greenfield, independently implemented Python Web/API framework.

It must not depend on Sanic, FastAPI, Flask, Django, Starlette, or another upper-level Web framework. The archived repository creates no compatibility obligation.

Any work that assumes migration of the legacy Sanic runtime, old API compatibility, or reuse of archived source/tests/scaffolding must stop and be reported as a scope conflict.

## Current phase

P0 is frozen. P1 is authorized by Final Freeze PR #51.

P1 follows the dependency graph in `docs/development/P1_IMPLEMENTATION_PLAN.md`. Only the active GitHub Issue authorizes writes. A later P1 task must not begin before its provider dependencies merge.

During P1-00, do not implement framework behavior assigned to P1-01 or later. Package markers and installed-version reporting are the only runtime-facing code allowed by Issue #52.

## Required reading order

Before writing, read:

1. `docs/development/DEVELOPMENT_CONSTITUTION.md`;
2. the active GitHub Issue and all scope-amendment comments;
3. `docs/development/CURRENT_PHASE.md`;
4. `docs/development/CONCURRENT_DEVELOPMENT.md`;
5. `docs/architecture/LINGSHU_FRAMEWORK_BLUEPRINT.md`;
6. applicable accepted ADRs under `docs/decisions/`;
7. `docs/development/P1_IMPLEMENTATION_PLAN.md`;
8. `docs/development/HANDOFF.md`;
9. the active branch and Pull Request.

Chat history, model memory, archived branches, closed legacy Issues, and old Pull Requests are not implementation authority.

When active sources conflict, stop. Do not guess which rule wins.

## Frozen package facts

```text
Canonical repository: qianhuaqi/lingshu
Distribution:         lingshu
Import package:       lingshu
Production source:    lingshu/
src layout:           prohibited
Build backend:        Hatchling
Version source:       static [project].version
First P1 version:     0.1.0.dev0
```

Do not create `src/lingshu/`, a second distribution, component-specific versions, duplicate manual `__version__` literals, or mandatory runtime dependencies without a new accepted decision.

## Task and concurrency rules

- One task uses one Issue, one writer-prefixed branch, one primary writer, one isolated worktree or clone, one virtual environment, and one Pull Request.
- Every Issue declares `base_commit`, `write_scope`, read dependencies, conflicts, integration order, exclusions, and required checks.
- Two active tasks with overlapping write scopes conflict by default.
- Provider contracts merge before consumers.
- Multiple developers must not write in the same worktree or branch.
- Development may be parallel only for explicitly independent scopes; integration into `main` is serial.
- Never copy uncommitted code, stashes, caches, runtime directories, or virtual environments between worktrees.

## Git and review workflow

- Never commit directly to `main`.
- Never force-push or rewrite shared history.
- Never enable automatic merge.
- Every commit requires a DCO `Signed-off-by` trailer; use `git commit -s`.
- Pull Requests must reference the active Issue and report actual changed paths, checks, evidence, risks, and remaining work.
- Implementation and acceptance remain separate.
- The project lead holds final merge authority.
- Update `HANDOFF.md` before switching developer, model, or computer.
- Never claim a check passed unless it was actually run.

## Architecture and dependency gate

The frozen Blueprint and accepted ADRs are implementation authority. A change to package layout, dependency direction, runtime semantics, public API, persistence format, protocol behavior, security, compatibility, or release policy requires a dedicated Issue and ADR.

- No upper-level Web framework may be added.
- Mandatory runtime dependencies require a dedicated dependency review/ADR.
- Optional tools and integrations must not become hidden runtime requirements.
- Production modules must not depend on `lingshu.testing`.
- Importing LingShu must not start tasks, open files, bind sockets, connect to services, or import user applications.

## Quality gate

Run the checks required by the active Issue. Applicable evidence includes unit, contract, integration, protocol, security, concurrency, leak, packaging, clean-install, and supported-platform checks.

Editable installation is not release evidence. Packaging-sensitive work must build wheel and sdist and test a non-editable wheel outside the repository checkout.

## Security gate

Never commit or reproduce real tokens, API keys, passwords, private keys, personal data, production endpoints, or production request bodies. Redact sensitive values from logs, records, examples, tests, Issues, Pull Requests, and diagnostics.

Unpatched vulnerabilities use the private process in `SECURITY.md`, never a public Issue.

## Legacy archive

The previous repository state is frozen at:

```text
archive/legacy-sanic-20260628
b869270e0ec7cbc324d17ef246e39d0873aab14f
```

Do not copy its source, tests, dependencies, compatibility rules, or public API assumptions into the greenfield implementation without an explicit Issue and architecture review.

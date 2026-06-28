# LingShu Development Constitution

- Status: Active
- Version: 3.0
- Effective baseline: P0 Final Freeze commit `4c925c20e53b5c3fc6005c5c07f2b32d5175a0f5`
- Applies to: all work in `qianhuaqi/lingshu`

## 1. Project identity

LingShu is a greenfield, independently implemented Python Web/API framework. It is not a wrapper, migration, adapter, or compatibility layer for Sanic, FastAPI, Flask, Django, Starlette, or another upper-level Web framework.

The legacy state is historical reference only at `archive/legacy-sanic-20260628`. Work assuming continuation of that runtime must stop as a scope conflict.

## 2. Authority and roles

The project lead decides scope, approves architecture changes, authorizes releases, may stop unsafe work, and holds final merge authority.

The architect prepares Issues and decisions, maintains phase documents, coordinates dependency order, and reviews implementation without silently changing confirmed product decisions.

A developer, human or AI:

- implements only the active Issue;
- writes only inside its declared scope;
- follows accepted dependencies and exclusions;
- supplies exact evidence;
- does not self-declare final acceptance;
- stops when fact sources or ownership conflict.

Implementation, independent review, and final merge remain separate responsibilities.

## 3. Sources of truth

When facts conflict, use this order:

1. explicit project-lead decision recorded in an accepted ADR or constitution amendment;
2. this constitution;
3. frozen Blueprint and accepted ADRs;
4. active GitHub Issue, including recorded scope amendments;
5. `CURRENT_PHASE.md`;
6. `CONCURRENT_DEVELOPMENT.md`;
7. active branch and Pull Request;
8. `HANDOFF.md`;
9. other documentation and examples.

The repository is authoritative; chat history, model memory, archives, and old Pull Requests are not. Conflicting active sources stop development until resolved in GitHub.

## 4. Phase and Issue lifecycle

Every task follows:

1. create one Issue with objective, value, scope, exclusions, base commit, writer, paths, dependencies, conflicts, integration order, deliverables, checks, risks, and acceptance;
2. create one writer-prefixed branch from the approved base;
3. use an isolated worktree or clone and virtual environment when work is concurrent;
4. implement only the Issue;
5. run and record required checks;
6. update handoff state when responsibility or device changes;
7. open one Pull Request;
8. perform independent review and resolve blocking findings;
9. obtain project-lead merge approval;
10. merge and synchronize phase state;
11. only then start dependent work.

No phase or dependency may be skipped. Planning may occur early only when the Issue explicitly marks it non-executable.

## 5. Branch, commit, and Pull Request rules

- Never commit directly to `main`.
- Never force-push or rewrite shared history.
- Never enable auto-merge.
- One branch has one primary writer.
- Concurrent writers use separate worktrees/clones, environments, caches, runtime directories, and ports.
- Every commit contains a DCO `Signed-off-by` trailer.
- Branch names identify writer and task, for example `human/dodo/p1-00-...`, `qwen/p1-...`, `glm/p1-...`, or `gemini/p1-...`.
- Pull Requests link the Issue and list base commit, writer, declared and actual paths, dependencies, checks, evidence, risks, and remaining work.
- Final merge authority belongs to the project lead.

Accidental direct commits or scope violations must be disclosed and corrected without unsafe history rewriting.

## 6. Concurrent ownership

Tasks are independent, ordered dependencies, conflicting, or cross-cutting exclusive.

Independent tasks may overlap only when paths and consumed contracts do not overlap. Ordered consumers wait for provider contracts to merge, synchronize with `main`, and rerun checks. Overlapping paths conflict by default. Cross-cutting packaging, CI, public export, lifecycle, security, or release changes permit one writer task at a time.

Active implementation commits are not cherry-picked between task branches unless both Issues record the reason and integration owner.

## 7. Frozen architecture and public contracts

P0 is frozen through ADR-001 to ADR-007. The implementation baseline is:

```text
one repository
one distribution: lingshu
one import package: lingshu
production source: lingshu/
no src/ directory
one version cadence
CPython >= 3.12
Hatchling and PEP 621
```

Changes affecting repository/package structure, dependency direction, runtime semantics, concurrency, public API, persistence, protocol behavior, security, compatibility, or release policy require a new Issue and ADR.

Public API consists only of documented exports and documented CLI, configuration, wire, metadata, and error-code contracts. Importable private names are not automatically public.

## 8. Dependency and import policy

- Upper-level Web frameworks are prohibited.
- A mandatory runtime dependency requires a dedicated ADR covering necessity, alternatives, security, maintenance, licensing, and fallback.
- Development tools remain optional and must not leak into runtime requirements.
- Optional integrations must not become hidden dependencies.
- Production code must not depend on `lingshu.testing`.
- Imports must not start tasks, bind sockets, open runtime files, connect to services, or import user applications.
- Do not copy dependency files or implementation from the archive.

## 9. Quality and evidence

Each Issue defines exact gates. Applicable work covers:

- unit and contract behavior;
- cross-component integration;
- malformed protocol and security cases;
- cancellation, timeout, cleanup, overload, race, and leak behavior;
- package boundaries and clean installation;
- supported Python/platform checks;
- matching documentation and examples.

Tests prove behavior, not field presence. Skipped, flaky, unavailable, or unrun checks must be disclosed. Editable installation is not release evidence.

Public code uses English identifiers, type annotations, useful docstrings, and design comments for complex ownership/security behavior. TODO/FIXME entries require an Issue and removal condition.

## 10. Security, compatibility, and release

Never commit credentials, keys, personal data, production endpoints, or sensitive request content. Diagnostics, records, logs, tests, and examples use safe placeholders and redaction.

Unpatched vulnerabilities follow `SECURITY.md` privately.

Compatibility and release work follows `RELEASE_AND_COMPATIBILITY_POLICY.md`. Published versions, tags, and artifacts are immutable. Public package publication requires separate project-lead authorization and is not implied by P1 completion.

## 11. Current P1 authority

P1 is the single-Worker minimum vertical slice in `P1_IMPLEMENTATION_PLAN.md`.

P1-00 creates package/tooling/CI foundations only. P1-01 through P1-10 start in provider-first order after prerequisites merge. Multi-Worker Supervisor, reload, advanced body/protocol features, official integrations, and public PyPI publication remain outside P1.

The active Issue controls current writes. Creating a future package directory does not authorize implementing its behavior early.

## 12. Handoff and deviations

Before switching computer, developer, or model:

1. stop writing;
2. run available required checks;
3. record unrun checks honestly;
4. confirm worktree status;
5. update `HANDOFF.md` with branch, commit, evidence, risks, and next action;
6. commit and push;
7. verify the remote branch.

A lasting deviation requires a written reason, affected rules, risks, scope, expiration where applicable, project-lead approval, and an ADR or constitution amendment when architectural.

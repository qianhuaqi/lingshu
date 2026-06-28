# LingShu Framework Target Directory Plan

- Status: Proposed
- Issue: #26
- Related decision: `docs/decisions/ADR-006-simplified-package-root-and-official-extensions.md`
- Applies to target state, not the current physical tree

## 1. Target repository tree

```text
sanic_framework/
├─ lingshu/                         # installable framework package
│  ├─ __init__.py                   # stable public facade
│  ├─ core/                         # mandatory dependency-light kernel
│  │  ├─ __init__.py
│  │  ├─ application.py             # application contracts and bootstrap state
│  │  ├─ lifecycle.py               # startup/shutdown lifecycle contracts
│  │  ├─ config.py                  # core configuration contracts
│  │  ├─ container.py               # service container contracts
│  │  ├─ context.py                 # execution/request context primitives
│  │  ├─ extension.py               # extension protocol and registry
│  │  ├─ exceptions.py              # framework base exception semantics
│  │  ├─ ids.py                     # request/operation ID abstractions
│  │  ├─ serialization.py           # shared serialization rules
│  │  ├─ time.py                    # system/monotonic time abstractions
│  │  ├─ telemetry.py               # telemetry contracts and standard fields
│  │  ├─ types.py                   # shared immutable types and protocols
│  │  └─ limits.py                  # resource-budget contracts
│  │
│  ├─ extensions/                   # official LingShu extensions
│  │  ├─ __init__.py
│  │  ├─ sanic/                     # Sanic adapter and request lifecycle
│  │  ├─ auth/                      # authentication capability
│  │  ├─ tenant/                    # optional tenant capability
│  │  ├─ database/                  # database capability and model integration
│  │  ├─ redis/                     # Redis capability
│  │  ├─ cache/                     # cache abstraction and providers
│  │  ├─ storage/                   # object/file storage capability
│  │  ├─ scheduler/                 # scheduled/background work capability
│  │  ├─ logging/                   # logging integration
│  │  └─ openapi/                   # OpenAPI/documentation integration
│  │
│  ├─ cli/                          # command-line application
│  │  ├─ commands/
│  │  └─ templates/                 # project scaffolding templates
│  │
│  ├─ testing/                      # helpers exposed to downstream projects
│  │
│  ├─ resources/                    # packaged non-code resources when required
│  └─ compat/                       # temporary compatibility shims only
│
├─ tests/                           # tests for LingShu repository itself
│  ├─ core/
│  ├─ extensions/
│  ├─ cli/
│  ├─ architecture/
│  └─ integration/
│
├─ docs/
│  ├─ architecture/
│  ├─ decisions/
│  ├─ development/
│  ├─ guides/
│  ├─ roadmap/
│  └─ examples/
│
├─ tools/                           # created only for real repository tools
├─ app/                             # development/example project owned by project layer
├─ config/                          # development/example project configuration
├─ pyproject.toml
├─ README.md
└─ AGENTS.md
```

The tree is a target, not an instruction to create every empty directory. Directories are introduced only with real code, tests, or documentation.

## 2. Permanent top-level areas

### `lingshu/`

Contains code and package resources distributed as LingShu Framework. Downstream business projects do not edit this directory.

### `tests/`

Contains verification for the LingShu repository. It is not shipped as a framework runtime area and is not the same as `lingshu/testing/`.

### `docs/`

Contains architecture, ADRs, development governance, guides, roadmaps, and runnable examples. A separate top-level `examples/` directory is not part of the target.

### `tools/`

Contains real repository tooling grouped by purpose, for example:

```text
tools/
├─ development/
├─ migration/
├─ quality/
└─ release/
```

`tools/` is optional. It must not be created as an empty placeholder or become an unclassified script dump.

### `app/` and `config/`

These remain project-owned areas used by the repository's development application and generated project contract. They are not part of the installable framework package.

## 3. `core` boundary

`lingshu/core/` is the smallest mandatory kernel. A module belongs in `core` only when all of the following are true:

1. the framework cannot define its basic runtime contracts without it;
2. it has no dependency on a concrete web framework, database, cache, JWT, storage, or scheduler implementation;
3. it can be tested without starting Sanic or external infrastructure;
4. official extensions may depend on it without creating a reverse dependency.

Expected responsibilities:

- application and lifecycle contracts;
- immutable configuration contracts and validation primitives;
- explicit execution-context primitives;
- extension protocol and registration lifecycle;
- base exception semantics;
- standard IDs and time abstractions;
- serialization contracts;
- telemetry field contracts;
- resource-limit and backpressure contracts;
- dependency-free shared types and protocols.

Forbidden in `core`:

- Sanic imports;
- PyJWT imports;
- MySQL/PostgreSQL/MongoDB/Redis drivers;
- MinIO or cloud storage SDKs;
- ORM implementations;
- project-specific user, permission, menu, tenant-data, or business models;
- imports from `lingshu.extensions`;
- compatibility implementations.

## 4. Official extension boundary

`lingshu/extensions/` contains capabilities maintained and released with LingShu.

Every official extension must define:

- its configuration object or schema;
- its install/register entry point;
- its runtime service(s);
- startup and shutdown behavior;
- health/readiness behavior where applicable;
- optional dependency declaration;
- public exports;
- isolated tests;
- failure and cleanup semantics.

An extension may be one of two classes:

### Runtime-required adapter

The Sanic adapter is required by the current LingShu product because LingShu is a Sanic framework. It still lives under `extensions/sanic/` so that Sanic cannot leak into `core`.

### Optional capability

Database, Redis, cache, tenant, storage, scheduler, and OpenAPI capabilities may be enabled only when a project installs/configures them.

## 5. Dependency direction

The mandatory direction is:

```text
core
  ↑
official extensions
  ↑
public facades / CLI / generated project
  ↑
downstream business application
```

Rules:

1. `core` never imports `extensions`.
2. An extension imports only public core contracts and explicitly approved extension dependencies.
3. Extension-to-extension dependencies must be declared, narrow, and cycle-free.
4. Cross-extension collaboration uses public protocols or services registered through the core extension registry.
5. Stable top-level facades may delegate to extensions but must not expose internal implementation paths.
6. `compat` may depend on legacy implementation details; permanent layers must not depend on `compat`.

## 6. Initial extension dependency policy

The following relationships are expected:

| Extension | May depend on | Must not depend on |
|---|---|---|
| `sanic` | `core`, public auth/tenant protocols | database drivers, compat |
| `auth` | `core`, approved JWT provider | Sanic internals, database implementation |
| `tenant` | `core`, public auth principal protocol | Sanic internals, concrete database implementation |
| `database` | `core`, database drivers | Sanic request globals, auth implementation |
| `redis` | `core`, Redis client | Sanic internals, database implementation |
| `cache` | `core`, cache provider protocols, optionally `redis` public service | Sanic internals, compat |
| `storage` | `core`, storage SDK | Sanic internals, database implementation |
| `scheduler` | `core`, declared service protocols | request-local context leakage |
| `logging` | `core` telemetry contracts | business application modules |
| `openapi` | `core`, approved Sanic public adapter API | database implementation, compat |

Exact machine allowlists are updated in the implementation phase that introduces each target directory.

## 7. Public facade policy

Existing Stable imports remain stable even when implementations move. Examples include:

```python
from lingshu import app, config, db, logger, request
from lingshu.auth import Principal, Authenticator
from lingshu.tenant import TenantContext, TenantResolver
from lingshu.router import RoutePolicy
from lingshu.model import Model, BaseModel, BusinessModel
```

A facade may delegate to a new official extension. It must not force downstream projects to import internal extension files unless that path is explicitly declared public.

## 8. Transitional directories

The following current or temporary areas are not assumed to survive as permanent v1 top-level package areas:

- `src/lingshu/` — current physical package root; moved in the package-layout release;
- `system/` — decomposed into `core` and official extensions;
- `middleware/` — legacy modules move to official extensions or `compat`;
- `model/` — split between database extension, public facade, and project-level conventions;
- `compat/` — retained only for the documented deprecation lifecycle;
- top-level `scripts/` — reviewed and migrated to classified `tools/` areas when the package-layout/tooling phase occurs.

No transitional directory is deleted merely because a target directory exists. Deletion requires consumer audit, API classification, migration documentation, and the existing deprecation rules.

## 9. Mapping from current architecture work

The reviewed C2-R1–R6 work is retained as technical input:

| Existing phase | Target interpretation |
|---|---|
| C2-R1 | legacy containment and compat shims before extension extraction |
| C2-R2 | split Sanic integration into `extensions/sanic` and extract dependency-free core primitives |
| C2-R3 | move tenant capability into `extensions/tenant` rather than permanent `contrib/tenant` |
| C2-R4 | unify route policy at public/core contract boundary |
| C2-R5 | modularize configuration by extension capability |
| C2-R6 | decouple model access and move infrastructure behavior into official data extensions |

The detailed release assignment is maintained in `docs/roadmap/RELEASE_ROADMAP.md`.

## 10. Physical migration rule

The package-root move is a dedicated release step:

```text
src/lingshu/  →  lingshu/
```

It must not be combined with major runtime behavior changes. The migration must update at least:

- `pyproject.toml` build/package discovery;
- editable-install behavior;
- CLI entry points;
- package data;
- scaffold template paths;
- architecture contracts and ownership roots;
- tests and import scanners;
- development and handoff tools;
- README and contributor setup instructions.

Public imports remain `lingshu.*` before and after the move.

## 11. Completion criteria for the target tree

The target directory plan is complete only when:

- the installable package exists directly at `lingshu/`;
- `core` passes machine checks proving it has no forbidden integrations;
- official extensions have explicit lifecycle and dependency contracts;
- current Stable imports remain valid;
- generated projects use public facades and official extension registration;
- all repository tests and package-build checks pass;
- documentation no longer describes `src/lingshu/` as the permanent target;
- transitional compatibility code is clearly classified and scheduled by policy.
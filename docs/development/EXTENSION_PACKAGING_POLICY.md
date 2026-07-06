# Official Extension Packaging and Dependency Policy

Status: draft for P4-05 review
Context: Issue #112

## 1. Purpose

This contract defines how official LingShu extensions are named, packaged, versioned, and constrained in P4.
It also defines the dependency model that keeps the core package thin while enabling official extensions to be added in later tracks.

It does **not** define runtime behavior for concrete external systems; it only defines package contracts and release discipline.

## 2. Non-goals

- Implementing Redis, MySQL, MongoDB extensions.
- Implementing identity/access extensions.
- Implementing OpenAPI generation.
- Implementing multi-worker mode, reload/watch mode, or adapter layers (ASGI/WSGI/WebSocket/HTTP2/HTTP3).
- Publishing a public package for any extension during P4.
- Making production-readiness or performance guarantees for extension packages.
- Adding mandatory runtime dependencies to `lingshu` core.

## 3. Naming and package boundary

## 3.1 Package names

Official extension packages use the suffix naming scheme:

- `lingshu-<name>` (for example `lingshu-redis`, `lingshu-mysql`)

The `<name>`:

- is lower-case.
- uses ASCII letters, digits, and hyphens only.
- is scoped to the domain represented by the package (data stores, identity, auth helpers, etc.).

## 3.2 Python package entry points

- Package root module namespace is free-form; avoid enforcing a global `lingshu.ext` import namespace in P4.
- Extensions must provide a stable integration surface explicitly documented in each extension package contract.
- Core integration remains through `lingshu.application.LingShu` extension hooks and official wrapper helpers.

## 4. Dependency policy

## 4.1 Core dependency floor

Every official extension package must declare a dependency on core:

- `lingshu >= 0.1.0, < 0.2.0` while on the P4 baseline

This keeps extension packages aligned to the P4 major baseline and makes breakage explicit when `LingShu` APIs change.

## 4.2 Runtime dependency policy

- `lingshu` must not add any new mandatory runtime dependency.
- Extension packages may add mandatory runtime dependencies only if required by their package boundary.
- Transport or client libraries required only for optional behaviors must be optional dependencies (`project.optional-dependencies`) and never be mandatory.
- P4 policy forbids introducing network drivers inside `lingshu` core to satisfy extension dependencies.

### 4.3 Optional dependency structure (recommended)

- Extension package may expose feature extras:
  - `redis`, `mysql`, `mongo`, `pools`, etc. where needed.
- Defaults should keep installation lightweight:
  - install `lingshu` + extension package gives a usable baseline,
  - extras opt into extra providers or adapters.
- Pin third-party packages conservatively (compatible ranges preferred), but do not over-constrain.

## 5. Version compatibility policy

### 5.1 Compatibility promise (P4 baseline)

- Core and extension public contracts are version-coupled only across major boundaries.
- Backward-compatible extension updates must use:
  - `>= 0.1.0,<0.2.0` for core constraint in this phase.
- Any API/ABI change to extension integration hooks must be surfaced in extension package docs before release.

### 5.2 Breaking-change behavior

- If extension API relies on optional hooks or behavior introduced in later minor versions, extension packages must:
  1. declare a tighter core lower-bound,
  2. gate execution paths by compatibility checks where needed,
  3. fail fast with an explicit, non-sensitive diagnostic.

## 6. Documentation boundary

Each official extension package must include:

- install instructions and optional extra usage;
- required/optional dependency table;
- accepted config schema and redaction class usage;
- startup/shutdown expectation (if resource based);
- failure and diagnostics contract references.

All extension docs should reference existing contracts:

- [Extension Contract](./EXTENSION_CONTRACT.md)
- [Resource Lifecycle Contract](./RESOURCE_LIFECYCLE_CONTRACT.md)
- [Configuration Redaction Contract](./CONFIGURATION_REDACTION_CONTRACT.md)

## 7. Security and diagnostics requirement

Official extension packages inherit existing LingShu diagnostic constraints:

- public reprs and logs must avoid secret leakage;
- errors visible to clients must use safe details conventions;
- extension `safe_details` payloads follow the same redaction and freeze model as core.

## 8. Testability and CI expectations for packaging

Each official extension package in P5 should provide:

- at least one minimal import smoke test,
- contract-oriented docs tests or examples (when available),
- clear dependency and config matrix for tested extras.

These checks are for future extension work; P4 only requires this contract to be explicit.

## 9. P5 preparation statement

P5 data extensions are expected to begin only after this policy and prior P4 contracts are accepted.

P5 concrete packages must include explicit migration notes for:

- configuration keys and redaction labels,
- dependency extras and installation commands,
- lifecycle ownership and failure contracts.

## 10. Contract references

- This policy is authoritative for P4-05 extension packaging decisions.
- [Extension Contract](./EXTENSION_CONTRACT.md)
- [P4 Roadmap](./P4_ROADMAP.md)

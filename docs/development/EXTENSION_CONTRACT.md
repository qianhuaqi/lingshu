# Official Extension Contract and Package Boundary

Status: draft for P4-02 review
Context: Issue #106

## 1. Goal

Define how official LingShu extensions (e.g., Redis, MySQL, MongoDB, Identity) are named, packaged, imported, and configured, without implementing concrete external dependencies in the core package.

## 2. Core Package and Naming Boundary

1. **Core Package (`lingshu`)**:
   - Contains the framework kernel, HTTP primitives, native single-worker server, routing, and extension interfaces.
   - ZERO mandatory runtime dependencies.
   - Must not contain concrete implementations for external data stores or protocols.

2. **Official Extension Packages (`lingshu-<extname>`)**:
   - Naming convention: `lingshu-<name>` (e.g., `lingshu-redis`, `lingshu-mysql`).
   - Import convention: `from lingshu.ext.<name> import ...` once an official namespace model is in place.
   - Official extension packages are packaged independently in later tracks.

## 3. Core Interface vs. Helper Classes

The framework provides core interfaces and typed contracts.
For detailed resource lifecycle integration (startup, shutdown, and cancellation requirements), refer to [Application Resource Lifecycle Contract](./RESOURCE_LIFECYCLE_CONTRACT.md).

For sensitive configuration discipline, extensions must follow:

- [Configuration Redaction Contract](./CONFIGURATION_REDACTION_CONTRACT.md)
- `lingshu.core.config.ConfigField.redaction`

Concretely:

- `lingshu.core.application` currently exposes `add_extension()` with `startup_hook` and `shutdown_hook`.
- A future `lingshu.ext` helper may provide a small `Extension` base class/Protocol, but current raw hook registration is sufficient.
- Decision: Core keeps registration contract in `app.add_extension(...)`; official extension packages may provide ergonomic setup wrappers (for example `setup_redis(app, config)`).
- Extensions MUST emit safe diagnostics and metadata for all redaction-labeled fields.

## 4. Extension Initialization and Configuration Handoff

1. **Registration Phase (CREATED / CONFIGURING)**:
   - Extensions are attached before application freeze.
   - Registration uses `app.add_extension(name="redis", dependencies=..., startup_hook=..., shutdown_hook=...)`.
   - Extensions MUST NOT open connections or start background tasks during registration.

2. **Configuration**:
   - Extensions receive configuration via the centralized `ConfigSnapshot` from `app.use_config(...)`.
   - Sensitive credentials (passwords, tokens, keys, DSNs) MUST follow [Configuration Redaction Contract](./CONFIGURATION_REDACTION_CONTRACT.md).
   - Logging and summary output from configuration handoff must use redacted snapshots, not raw values.

3. **Lifecycle Phase (STARTING / RUNNING / STOPPING)**:
   - `startup_hook` is called by the application kernel in dependency order for connection/handle setup.
   - `shutdown_hook` is called in reverse dependency order during shutdown.
   - Lifecycle diagnostics must keep extension metadata safe under the same redaction rules.

## 5. Compatibility Expectations

- Official extension packages must publish compatible ranges against core, e.g., `lingshu >= 0.1.0, < 0.2.0`.
- Changes to `ExtensionContribution`, lifecycle registration, or startup/shutdown ordering are treated as compatibility-sensitive in core.

## 6. Pre-requisites for P5 Data Extensions

Before concrete data extensions can begin in P5, the following P4 tasks MUST be complete:

- **P4-03**: Application resource lifecycle contract.
- **P4-04**: Configuration redaction contract for extensions.
- **P4-05**: Official extension packaging and dependency policy.

## 7. Redaction checkpoints for P5

Concrete extension tracks must provide evidence for:

- explicit `ConfigField.redaction` definitions for sensitive fields;
- redacted diagnostic paths in setup and runtime reporting;
- safe `safe_details` and frozen safe detail payloads for extension-originated failures.

## 8. Prohibitions and Deferred Tracks

- Concrete data store implementations (Redis, MySQL, MongoDB).
- Identity and access implementations.
- OpenAPI generation.
- Multi-worker supervisors or reload/watch features.
- ASGI / WSGI / WebSocket / HTTP2 / HTTP3 adapters.
- Public package publication to PyPI during P4-04.
- Production-ready or performance claims.
- New mandatory runtime dependencies.

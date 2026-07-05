# Official Extension Contract and Package Boundary

Status: accepted by P4-02
Context: Issue #106

## 1. Goal

Define how official LingShu extensions (e.g., Redis, MySQL, MongoDB, Identity) are named, packaged, imported, and configured, without implementing any concrete external dependencies in the core package.

## 2. Package Boundary and Naming

1. **Core Package (`lingshu`)**:
   - Contains ONLY the framework kernel, HTTP primitives, native single-worker server, routing, and extension interfaces.
   - ZERO mandatory runtime dependencies.
   - Must not contain concrete implementations for external data stores or protocols (e.g., Redis client, MySQL driver).

2. **Official Extension Packages (`lingshu-<extname>`)**:
   - Naming convention: `lingshu-<name>` (e.g., `lingshu-redis`, `lingshu-mysql`).
   - Import convention: `from lingshu.ext.<name> import ...` (via implicit namespace packages or standard subpackages if unified). 
   - Distributed as independent PyPI packages. They declare `lingshu` as a dependency.
   - Example: `pip install lingshu-redis` -> provides `lingshu.ext.redis`.

## 3. Core Interface vs. Helper Classes

The core framework will provide minimal **Protocols and Helper Base Classes** to ensure consistent developer experience across extensions. 

- `lingshu.core.application` currently exposes `add_extension()` with raw `startup_hook` and `shutdown_hook`.
- A future or minimal `lingshu.ext` module may provide an `Extension` base class or Protocol. However, currently, the raw hook registration is sufficient to establish lifecycle boundaries.
- **Decision**: Core provides the registration contract (`ExtensionContribution` via `app.add_extension`). Official extensions may wrap this in user-friendly setup functions (e.g., `setup_redis(app, config)`), which internally call `app.add_extension(...)`.

## 4. Extension Initialization and Configuration Handoff

1. **Registration Phase (CREATED / CONFIGURING)**:
   - Extensions are attached before application freeze.
   - They register via `app.add_extension(name="redis", dependencies=..., startup_hook=..., shutdown_hook=...)`.
   - Extensions must NOT open connections or start background tasks during registration.

2. **Configuration**:
   - Extensions receive configuration via the centralized `ConfigSnapshot` when `app.use_config(...)` is called.
   - A dedicated configuration redaction contract (P4-04) will define how sensitive credentials (passwords, tokens) are handled.

3. **Lifecycle Phase (STARTING / RUNNING / STOPPING)**:
   - `startup_hook` is called by the application kernel in dependency order. This is where connection pools are created.
   - `shutdown_hook` is called in reverse dependency order during shutdown to gracefully close pools.

## 5. Compatibility Expectations

- Official extensions must declare strict compatibility ranges with the core package (e.g., `lingshu >= 0.1.0, < 0.2.0`).
- Core framework upgrades must treat changes to the `ExtensionContribution` and lifecycle hooks as major breaking changes.

## 6. Pre-requisites for P5 Data Extensions

Before any concrete data extensions (Redis, MySQL, MongoDB) can begin in P5, the following P4 tasks MUST be completed:
- **P4-03**: Application resource lifecycle contract.
- **P4-04**: Configuration redaction contract for extensions.
- **P4-05**: Official extension packaging and dependency policy.

## 7. Prohibitions and Deferred Tracks

The following remain explicitly PROHIBITED in the core package and during P4:
- Concrete data store implementations (Redis, MySQL, MongoDB).
- Identity and access implementations.
- OpenAPI generation.
- Multi-worker supervisors or reload/watch features.
- ASGI / WSGI / WebSocket / HTTP2 / HTTP3 adapters.
- Public package publication to PyPI.
- Production-ready or performance claims.
- Any new mandatory runtime dependencies.

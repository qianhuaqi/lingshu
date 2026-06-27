# src Target Boundaries

Phase: C2-R0
Issue: #19

## 1. Target Directory Structure

```
src/lingshu/
├── core/                         Framework core — zero framework deps
│   ├── __init__.py
│   ├── context.py                ContextVar management (app/request/user)
│   ├── execution.py              RequestExecutionContext (deadline, cancel)
│   ├── errors.py                 Framework exception hierarchy
│   ├── types.py                  Shared types: _deep_freeze, Binding protocol
│   └── policy.py                 RoutePolicyDefinition + CompiledRoutePolicy
│
├── adapters/
│   └── sanic/                    Sanic-specific adapter layer
│       ├── __init__.py
│       ├── context_middleware.py install_context_middleware + request lifecycle
│       ├── resource_registry.py  set_resource/get_resource/get_app_config
│       ├── finalize.py           finalize_request_context + cleanup
│       ├── health.py             install_health_routes
│       ├── lifecycle.py          ApplicationLifecycle + ShutdownCoordinator
│       └── policy_compiler.py    RoutePolicyCompiler (Sanic route traversal)
│
├── security/
│   ├── auth/                     Authentication (no tenant dependency)
│   │   ├── __init__.py
│   │   ├── principal.py          Principal frozen dataclass
│   │   ├── result.py             AuthResult + AuthenticationOutcome
│   │   ├── authenticator.py      Authenticator Protocol + AuthenticatorChain
│   │   ├── context.py            Principal ContextVar binding
│   │   ├── jwt_bearer.py         JwtBearerAuthenticator
│   │   ├── middleware.py         Auth fail-closed middleware
│   │   └── stub_authenticator.py Test-only
│   │
│   └── authorization/            Future: RBAC, scopes, permissions (C3+, not now)
│       └── __init__.py           Placeholder
│
├── contrib/
│   └── tenant/                   Optional tenant resolution module
│       ├── __init__.py
│       ├── context.py            TenantContext frozen dataclass
│       ├── result.py             TenantResolutionResult + Outcome
│       ├── resolver.py           TenantResolver Protocol + Chain
│       ├── binding.py            TenantContext ContextVar binding
│       ├── claim_resolver.py     ClaimTenantResolver
│       ├── middleware.py         Tenant fail-closed middleware
│       └── stub_resolver.py      Test-only
│
├── data/                         Data access layer
│   ├── __init__.py
│   ├── database/                 Database wrappers (mysql, redis, mongo)
│   ├── model/                    ORM layer (BaseModel, Model, BusinessModel)
│   └── dependencies.py           Optional driver import guard
│
├── compat/                       Legacy compatibility layer
│   ├── __init__.py
│   ├── auth.py                   Legacy Auth/token_required shim
│   ├── signing.py                Legacy sign_required shim
│   ├── maintenance.py            Legacy maintenance_required shim
│   ├── cache.py                  Legacy Cache (dead code, minimal shim)
│   ├── params.py                 Legacy I()/CI() parameter accessors
│   ├── crypt.py                  DES encryption (crypt_des, crypt_params)
│   └── json_encoder.py           CustomJSONEncoder
│
├── public/                       Public API facades (re-exports)
│   ├── __init__.py               lingshu.* top-level exports
│   ├── auth.py                   lingshu.auth facade
│   ├── tenant.py                 lingshu.tenant facade
│   ├── request.py                RequestProxy + global `request`
│   ├── config.py                 ConfigProxy + global `config`
│   ├── app.py                    AppProxy + global `app`
│   ├── db.py                     DatabaseProxy + global `db`
│   └── logger.py                 LoggerProxy + global `logger`
│
├── app.py                        Application factory (composition only)
├── response.py                   json_response()
├── exception.py                  APIException + get_error_message
├── error_codes.py                Error-code catalog
├── versioning.py                 API version parsing
├── config.py                     AppConfig + load_config (slimmed in R5)
├── logging.py                    setup_logging()
├── middleware_registry.py        CORS + request-id middleware
├── controller.py                 Request payload helpers
├── helper.py                     write_verify_log
├── runtime.py                    run_app()
│
├── cli/
│   ├── main.py
│   └── project.py
│
├── scaffold/
│   └── *.j2
│
├── resources/
│   └── error_codes/modules.ini
│
└── view/
    └── __init__.py
```

## 2. Layer Responsibilities and Dependency Rules

### 2.1 `core/` — Framework Foundation

**Responsibility:** Pure Python types, ContextVar management, execution context,
route policy data structures. No knowledge of any web framework, database driver,
or security implementation.

| Rule | Detail |
|---|---|
| **May import** | Standard library only |
| **Must NOT import** | Sanic, JWT, database drivers, `adapters/`, `security/`, `contrib/`, `data/`, `compat/` |
| **Public API** | `ContextVars`, `RequestExecutionContext`, `RoutePolicyDefinition`, `CompiledRoutePolicy`, `_deep_freeze`, `Binding` protocol |
| **Lifecycle** | Module-level constants; ContextVar tokens managed by adapters |
| **Testing** | Pure unit tests, no fixtures needed |

### 2.2 `adapters/sanic/` — Sanic Integration

**Responsibility:** Bridge between core types and Sanic's request/response lifecycle.
Installs middleware, manages request context binding/finalization, compiles route
policies by traversing Sanic's router, provides health endpoints.

| Rule | Detail |
|---|---|
| **May import** | `core/`, `response.py`, `exception.py` |
| **Must NOT import** | `security/`, `contrib/`, `data/`, `compat/`, Sanic at module level (duck-typed via `raw_app` parameter) |
| **Public API** | `install_context_middleware`, `finalize_request_context`, `set_resource`/`get_resource`, `install_health_routes`, `RoutePolicyCompiler` |
| **Lifecycle** | Installed by `app.py` at startup; middleware functions are closures over `raw_app` |
| **Cleanup** | `finalize_request_context` is the single cleanup entry point; it must call into binding resetters registered by security/contrib layers via a registry, not by hardcoding attribute names |

**Key design change:** Instead of `sanic_adapter.py` hardcoding `_reset_principal_binding` and `_reset_tenant_binding`, the adapter should maintain a **cleanup registry** where auth and tenant modules register their reset functions. This breaks the `system -> auth/tenant` coupling.

```python
# adapters/sanic/finalize.py concept
_cleanup_hooks: list[Callable] = []

def register_cleanup_hook(hook: Callable):
    _cleanup_hooks.append(hook)

async def finalize_request_context(raw_request, *, reason=None):
    for hook in _cleanup_hooks:
        await hook(raw_request)
    # ... core cleanup
```

### 2.3 `security/auth/` — Authentication

**Responsibility:** Identity verification (who is the caller?). Implements
Authenticator protocol, chain, JWT bearer, fail-closed middleware.

| Rule | Detail |
|---|---|
| **May import** | `core/`, `adapters/sanic/` (for middleware install + finalize) |
| **Must NOT import** | `contrib/tenant/`, `data/`, `compat/` |
| **Public API** | `Principal`, `Authenticator`, `AuthenticatorChain`, `JwtBearerAuthenticator`, `AuthenticationOutcome`, `configure_authentication` |
| **Lifecycle** | Middleware installed by `app.py`; chain set by `configure_authentication` |
| **Binding cleanup** | Registers cleanup hook with `adapters/sanic/finalize.py` at import time |

### 2.4 `contrib/tenant/` — Optional Tenant Resolution

**Responsibility:** Tenant identity resolution (which tenant does this request belong to?).
Implements TenantResolver protocol, chain, claim-based resolver, fail-closed middleware.

| Rule | Detail |
|---|---|
| **May import** | `core/`, `adapters/sanic/`, `security/auth/` (needs Principal) |
| **Must NOT import** | `data/`, `compat/` |
| **Public API** | `TenantContext`, `TenantResolver`, `TenantResolverChain`, `ClaimTenantResolver`, `configure_tenant_resolution` |
| **Lifecycle** | Middleware installed by `app.py` unconditionally; chain set by `configure_tenant_resolution` |
| **Optionality** | If no chain is registered, tenant-required routes return 403/990124. Non-tenant routes are unaffected. |
| **Binding cleanup** | Registers cleanup hook with `adapters/sanic/finalize.py` |

**Tenant is NOT inside `security/auth/`.** It depends on auth (Principal), but auth does not depend on tenant. This preserves the one-way dependency: `tenant -> auth -> core`.

### 2.5 `data/` — Data Access

**Responsibility:** Database wrappers (MySQL, Redis, MongoDB) and ORM layer
(BaseModel, Model, BusinessModel).

| Rule | Detail |
|---|---|
| **May import** | `core/` (for ContextVar access in Model), standard library, third-party drivers (aiomysql, motor, redis) |
| **Must NOT import** | `adapters/sanic/`, `security/`, `contrib/`, Sanic |
| **Global proxies** | `Model` and `BusinessModel` currently import `lingshu.db` and `lingshu.request` — this must be refactored to receive `db`/`request` as parameters (R6 goal) |
| **Public API** | `BaseModel`, `Model`, `BusinessModel`, `MySQLDatabase`, `RedisManager`, `MongoDB` |

### 2.6 `compat/` — Legacy Compatibility

**Responsibility:** Shim layer preserving old API surface for existing user projects.

| Rule | Detail |
|---|---|
| **May import** | Legacy implementations (which may import anything) |
| **Must NOT be imported by** | `core/`, `adapters/`, `security/`, `contrib/`, `data/`, `app.py` |
| **Public API** | `Auth`, `token_required`, `I`, `CI`, `sign_required`, `maintenance_required`, `CustomJSONEncoder` |
| **Lifecycle** | These shims exist for one compat cycle (C2-R1 through C3). After C3 acceptance, they are removed. |
| **New code** | Must NOT use `compat/` — only existing user projects transitioning to the new framework version need it. |

### 2.7 `public/` — Public Facade Layer

**Responsibility:** Stable public API surface. Business code imports from
`lingshu.auth`, `lingshu.tenant`, `from lingshu import request`, etc.

| Rule | Detail |
|---|---|
| **May import** | `core/`, `security/`, `contrib/`, `adapters/` |
| **Must NOT import** | `data/` (db proxy is an exception — it lazy-imports from adapters), `compat/` |
| **Public API** | Everything in `__all__` |
| **Constraint** | Business code must never import `lingshu.system` or `lingshu.adapters` directly |

### 2.8 `app.py` — Application Factory

**Responsibility:** Composition root. Creates Sanic app, installs middleware,
registers blueprints, wires lifecycle. Contains zero business logic.

| Rule | Detail |
|---|---|
| **May import** | Everything |
| **Must NOT** | Define business logic, data transformations, or domain-specific behavior |

## 3. Cleanup Hook Registry Pattern

The current `sanic_adapter.py` hardcodes knowledge of auth and tenant bindings:

```python
# Current (bad):
def reset_request_context(raw_request):
    # ... reset core tokens ...
    _reset_principal_binding(raw_request)
    _reset_tenant_binding(raw_request)
```

Target: cleanup hooks registered by each subsystem:

```python
# adapters/sanic/finalize.py
_cleanup_hooks: list[Callable[[Any], Awaitable[None]]] = []

def register_request_cleanup(hook):
    _cleanup_hooks.append(hook)

async def finalize_request_context(raw_request, *, reason=None):
    for hook in _cleanup_hooks:
        try:
            await hook(raw_request)
        except Exception:
            pass  # logged, not leaked
    # ... core context reset ...
```

```python
# security/auth/context.py
from lingshu.adapters.sanic.finalize import register_request_cleanup

async def _cleanup_principal(raw_request):
    binding = getattr(raw_request.ctx, "lingshu_principal_binding", None)
    if binding and not binding.reset_done:
        binding.__exit__(None, None, None)

register_request_cleanup(_cleanup_principal)
```

This breaks the bidirectional coupling: `adapters/` no longer knows about
`security/` or `contrib/` internals.

## 4. Tenant Module Positioning

Tenant resolution is an **optional contrib module**, not part of core auth.

- **Current location:** `system/auth/tenant/` (implies tenant is a sub-concern of auth)
- **Problem:** This couples auth with tenant conceptually. Auth must work without tenant.
- **Target:** `contrib/tenant/` — a standalone module that *depends on* auth (needs
  Principal) but is not *part of* auth.
- **Migration path:** C2-R3 moves the directory; public API (`lingshu.tenant`)
  remains unchanged.

## 5. Legacy/Compat Rules

| Legacy module | Compat shim location | Removal target |
|---|---|---|
| `middleware/auth.py` | `compat/auth.py` | After C3 |
| `middleware/sign.py` | `compat/signing.py` | After C3 |
| `middleware/maintenance.py` | `compat/maintenance.py` | After C3 |
| `middleware/cache.py` | (delete — no consumers) | C2-R1 |
| `middleware/params.py` (`I`) | `compat/params.py` | After C3 |
| `middleware/crypt_des.py` | `compat/crypt.py` | After C3 |
| `middleware/crypt_params.py` (`CI`) | `compat/params.py` | After C3 |
| `middleware/json.py` | `compat/json_encoder.py` | After C3 |
| `middleware/utils.py` (md5, ip) | `compat/utils.py` or merge into `core/types.py` | After C3 |

New code must never import from `compat/`. The CLI linter (`cli/project.py`)
should be extended to flag `lingshu.compat` imports in user project code.

# src Convergence Audit

Phase: C2-R0
Issue: #19
Branch: research/c2-src-convergence
Baseline: 446 passed, 1 skipped, 0 failed

## 1. Current Directory Structure

```
src/lingshu/
├── __init__.py              (22 LOC)  Facade: abort, language, proxies
├── app.py                   (88 LOC)  Application factory create_app()
├── auth.py                  (75 LOC)  Public auth facade (re-exports system.auth)
├── config.py               (307 LOC)  AppConfig + load_config() + module facade
├── controller.py            (19 LOC)  Request payload helpers (require_mysql, etc.)
├── error_codes.py          (416 LOC)  Error-code catalog parsing/validation
├── exception.py             (56 LOC)  APIException + get_error_message
├── helper.py                (20 LOC)  write_verify_log + exists_path
├── i18n.py                  (32 LOC)  sanic_babel setup + ini i18n parser
├── lifecycle.py             (59 LOC)  Wiring: registers system.lifecycle onto app
├── logging.py               (64 LOC)  setup_logging() + request-context filter
├── middleware_registry.py   (48 LOC)  CORS + X-Request-ID middleware
├── response.py              (10 LOC)  json_response() unified builder
├── router.py                (20 LOC)  RoutePolicy + blueprint registration
├── runtime.py                (7 LOC)  run_app() entry point
├── tenant.py                (54 LOC)  Public tenant facade (re-exports system.auth.tenant)
├── versioning.py            (16 LOC)  API version parsing from URL path
│
├── cli/
│   ├── __init__.py           (1 LOC)
│   ├── main.py             (289 LOC)  CLI entry: init, add, make, check
│   └── project.py          (557 LOC)  Scaffold engine + project linter (AST)
│
├── database/
│   ├── __init__.py           (4 LOC)  Re-exports MongoDB, MySQLDatabase, RedisManager
│   ├── dependencies.py      (25 LOC)  Optional driver import guard
│   ├── mongo.py             (90 LOC)  Motor async MongoDB wrapper
│   ├── mysql.py            (150 LOC)  aiomysql wrapper with read-splitting
│   └── redis.py            (322 LOC)  Redis async client with Sentinel support
│
├── extensions/
│   ├── __init__.py           (0 LOC)
│   ├── auth.py               (4 LOC)  Re-export middleware.auth (LEGACY)
│   ├── cache.py              (4 LOC)  Re-export middleware.cache (DEAD)
│   ├── i18n.py               (4 LOC)  Re-export lingshu.i18n (UNUSED)
│   ├── maintenance.py        (4 LOC)  Re-export middleware.maintenance (LEGACY)
│   ├── mongo.py             (19 LOC)  MongoDB lifecycle hook (ACTIVE)
│   ├── mysql.py             (19 LOC)  MySQL lifecycle hook (ACTIVE)
│   ├── redis.py             (18 LOC)  Redis lifecycle hook (ACTIVE)
│   ├── registry.py          (44 LOC)  Extension orchestrator (ACTIVE)
│   └── signing.py            (4 LOC)  Re-export middleware.sign (LEGACY)
│
├── middleware/
│   ├── __init__.py           (8 LOC)  init_app stub (UNUSED)
│   ├── auth.py             (161 LOC)  Legacy JWT auth (Auth, token_required)
│   ├── cache.py            (114 LOC)  Filesystem cache (DEAD)
│   ├── crypt_des.py         (49 LOC)  DES-CBC encryption (LEGACY ACTIVE)
│   ├── crypt_params.py      (97 LOC)  Encrypted param accessor CI (LEGACY ACTIVE)
│   ├── json.py              (13 LOC)  CustomJSONEncoder (ACTIVE)
│   ├── maintenance.py       (61 LOC)  Maintenance decorator (LEGACY)
│   ├── params.py           (117 LOC)  Param accessor I() (LEGACY ACTIVE)
│   ├── sign.py              (69 LOC)  Sign verification decorator (LEGACY)
│   └── utils.py            (101 LOC)  Mixed utilities (md5, ip, legacy json_response)
│
├── model/
│   ├── __init__.py           (4 LOC)  Re-exports BaseModel, BusinessModel, Model
│   ├── base.py             (416 LOC)  Active-record ORM engine (SQL builder + cache)
│   ├── business.py          (30 LOC)  Non-table business logic mixin (uses globals)
│   └── model.py            (214 LOC)  Instance-based compat Model (soft-delete, timestamps)
│
├── resources/
│   └── error_codes/
│       └── modules.ini                Canonical error-code module registry
│
├── scaffold/
│   ├── business_model.py.j2
│   ├── controller.py.j2
│   ├── docker-compose.yml.j2
│   ├── docs.md.j2
│   ├── env.example.j2
│   ├── pyproject.toml.j2
│   ├── README.md.j2
│   ├── table_model.py.j2
│   └── view.html.j2
│
├── system/
│   ├── __init__.py           (1 LOC)
│   ├── context.py           (97 LOC)  ContextVar management (app/request/user)
│   ├── errors.py            (11 LOC)  Framework exception hierarchy
│   ├── execution.py        (119 LOC)  RequestExecutionContext (deadline, cancel)
│   ├── lifecycle.py        (231 LOC)  Lifecycle state machine + health routes
│   ├── policy.py           (198 LOC)  RoutePolicyDefinition + compiler
│   ├── proxies.py          (105 LOC)  Global proxies (logger, config, app, request, db)
│   ├── registry.py           (3 LOC)  Re-export sanic_adapter resource functions
│   ├── resources.py          (3 LOC)  Re-export db proxy
│   ├── sanic_adapter.py    (284 LOC)  Sanic adapter (context, finalize, middleware)
│   ├── tasks.py            (233 LOC)  Background task registry + lifecycle
│   └── auth/
│       ├── __init__.py      (44 LOC)  Internal auth module aggregation
│       ├── authenticator.py (88 LOC)  Authenticator Protocol + Chain
│       ├── context.py       (52 LOC)  Principal ContextVar binding
│       ├── jwt_bearer.py   (157 LOC)  JWT Bearer authenticator (PyJWT)
│       ├── jwt_test_helpers.py (52 LOC)  Test-only JWT token generation
│       ├── middleware.py   (135 LOC)  Auth fail-closed middleware
│       ├── principal.py     (78 LOC)  Principal frozen dataclass
│       ├── result.py       (124 LOC)  AuthResult enum + AuthenticationOutcome
│       ├── stub_authenticator.py (73 LOC)  Test stub
│       └── tenant/
│           ├── __init__.py   (0 LOC)
│           ├── binding.py   (48 LOC)  TenantContext ContextVar binding
│           ├── claim_resolver.py (119 LOC)  Claim-based resolver
│           ├── context.py   (63 LOC)  TenantContext frozen dataclass
│           ├── middleware.py (120 LOC)  Tenant fail-closed middleware
│           ├── resolver.py  (78 LOC)  TenantResolver Protocol + Chain
│           ├── result.py    (90 LOC)  TenantResolutionResult + Outcome
│           └── stub_resolver.py (53 LOC)  Test stub
│
└── view/
    └── __init__.py           (1 LOC)  Placeholder package
```

Total: ~50 .py files, ~5,100 LOC (excluding scaffold templates and .ini).

## 2. New vs Legacy Overlap Matrix

| Concern | New (system/) | Legacy (middleware/ + extensions/) | Status |
|---|---|---|---|
| **Authentication** | `system.auth.*` (AuthenticatorChain, JwtBearer, middleware) | `middleware/auth.py` (Auth, token_required) | Legacy superseded; re-exported via `extensions/auth.py` |
| **Signing** | `system.policy.RoutePolicyDefinition` (signing not yet migrated) | `middleware/sign.py` (sign_required decorator) | Legacy re-exported via `extensions/signing.py`; active signing in `RoutePolicy.signing_required` |
| **Maintenance** | `system.lifecycle.ApplicationLifecycle` + health routes | `middleware/maintenance.py` (maintenance_required decorator) | Legacy re-exported via `extensions/maintenance.py` |
| **Caching** | (none) | `middleware/cache.py` (filesystem cache) | Dead code — no consumers |
| **Response** | `response.json_response()` | `middleware/utils.json_response()` | Signature collision: legacy takes `(request, data, code, msg, **kwargs)`, active takes `(data, code, msg, status)` |
| **RoutePolicy** | `system.policy.RoutePolicyDefinition` (7 fields) | `router.RoutePolicy` (4 fields) | `from_legacy()` bridges; `signing_required` field lost in transition |
| **Context** | `system.context.*` + `system.execution.*` | `middleware_registry.py` (request_id + CORS) | Orthogonal: different middleware layers, but both write `request.ctx.*` |
| **i18n** | `exception.py` → `error_codes.py` (ini-based) | `i18n.py` (sanic_babel) + `extensions/i18n.py` | `setup_i18n()` never called by `create_app()` |

## 3. Dependency Analysis

### 3.1 Circular Dependency

**Confirmed: `exception <-> system`** (package level)

- `exception.py` imports `lingshu.system.context` and `lingshu.system.sanic_adapter`
- `system/sanic_adapter.py` imports `lingshu.response` (which has no deps)
- `system/lifecycle.py` imports `lingshu.response` directly
- `system/policy.py` has a lazy import to `lingshu.system.sanic_adapter`

The cycle is currently broken by lazy imports (function-level `from lingshu.exception import ...`), but it is a structural smell.

### 3.2 Lazy Imports (function-level deferred imports)

Lazy imports are used as cycle-breaking workarounds in 18 locations across 15 files:

| File | Lazy target | Why deferred |
|---|---|---|
| `app.py` | `system.auth.middleware`, `system.auth.tenant.middleware` | Avoid import at module load |
| `app.py` | `system.context` | Circular with exception |
| `auth.py` | `system.auth.middleware`, `system.execution`, `system.auth.context` | Facade defers heavy imports |
| `config.py` | `system.context`, `system.sanic_adapter` | Facade pattern |
| `runtime.py` | `system.sanic_adapter` | Avoid circular |
| `tenant.py` | `system.auth.tenant.middleware`, `system.execution`, `system.auth.tenant.binding` | Facade defers heavy imports |
| `system/lifecycle.py` | `system.policy` | Avoid circular |
| `system/policy.py` | `system.sanic_adapter` | Avoid circular |
| `system/proxies.py` | `system.auth.context`, `system.auth.tenant.binding` | Avoid importing auth/tenant at system level |
| `system/sanic_adapter.py` | `system.tasks` | Avoid circular |
| `system/auth/middleware.py` | `lingshu.exception`, `system.sanic_adapter` | Avoid circular |
| `system/auth/tenant/middleware.py` | `lingshu.exception`, `system.auth.context`, `system.sanic_adapter` | Avoid circular |

### 3.3 Cross-Subsystem Coupling

- **system -> auth/tenant**: `sanic_adapter.py` directly references `lingshu_principal_binding` and `lingshu_tenant_binding` in `reset_request_context()` and `detach_request_context_after_task()`. This is the only file outside auth/tenant that knows about these binding attributes.
- **proxies -> auth/tenant**: `RequestProxy.principal` and `RequestProxy.tenant` use lazy imports to access auth/tenant bindings.
- **auth -> tenant**: None (clean).
- **tenant -> auth**: `claim_resolver.py` and `stub_resolver.py` import `Principal` from auth (correct — tenant resolution depends on authenticated identity).

### 3.4 Hot Files (top 10 by LOC)

| Rank | File | LOC | Concerns |
|---|---|---|---|
| 1 | `cli/project.py` | 557 | Scaffold engine + AST linter (overloaded) |
| 2 | `error_codes.py` | 416 | Catalog parser + validator |
| 3 | `model/base.py` | 416 | SQL builder + cache + active-record |
| 4 | `system/sanic_adapter.py` | 284+ (varies) | God module: config, context, finalize, middleware, routing, cleanup |
| 5 | `database/redis.py` | 322 | Redis client (Sentinel + direct) |
| 6 | `config.py` | 307 | AppConfig + env parsing + module facade |
| 7 | `cli/main.py` | 289 | CLI argument dispatch |
| 8 | `system/lifecycle.py` | 231 | Lifecycle + health + shutdown |
| 9 | `system/tasks.py` | 233 | Task registry + sanitization |
| 10 | `system/policy.py` | 198 | Route policy compiler |

### 3.5 Reverse Dependency Hotspots

`system` is imported by 16 other packages — it is the most depended-upon subsystem.

`exception` is imported by 5 packages (including system itself — the circular dependency).

`middleware` is imported by 4 packages (extensions, helper, middleware self, model).

## 4. `_deep_freeze` Triplication

The same recursive freeze function is copy-pasted in three locations:
1. `system/proxies.py` (`_freeze_value`)
2. `system/auth/principal.py` (`_deep_freeze`)
3. `system/auth/tenant/context.py` (`_deep_freeze`)

All three are functionally identical (dict→MappingProxyType, list→tuple, set→frozenset, recursive).

## 5. Binding Pattern Repetition

Four nearly identical ContextVar binding implementations:
1. `system/context.py` — `_ContextTokens` (4 ContextVars)
2. `system/execution.py` — `_ExecutionBinding` (1 ContextVar)
3. `system/auth/context.py` — `_PrincipalBinding` (1 ContextVar)
4. `system/auth/tenant/binding.py` — `_TenantBinding` (1 ContextVar)

Items 2-4 are structurally identical: `__enter__`/`__exit__`/`reset`/`detach_after_task` with `reset_done` tracking.

## 6. Legacy Code Inventory

| Module | Status | Consumers | Recommendation |
|---|---|---|---|
| `middleware/__init__.py` (`init_app`) | Dead | None | Delete in R1 |
| `middleware/auth.py` (`Auth`, `token_required`) | Legacy | `app/__init__.py` re-export, `extensions/auth.py` | Compat shim in R1, deprecate |
| `middleware/cache.py` (`Cache`) | Dead | None (re-exported by `extensions/cache.py` but no callers) | Delete in R1 |
| `middleware/maintenance.py` | Legacy | `extensions/maintenance.py` (test only) | Compat in R2 |
| `middleware/sign.py` | Legacy | `extensions/signing.py` (test only); `RoutePolicy.signing_required` is unrelated | Compat in R2 |
| `middleware/utils.py` (`json_response`) | Shadowed | None — superseded by `lingshu.response.json_response` | Delete legacy `json_response`, keep `md5`/`get_client_ip` |
| `middleware/utils.py` (`filter_zjh`, `get_nonce_str`, etc.) | Dead | None | Delete in R1 |
| `extensions/auth.py` | Legacy facade | `tests/test_security_extensions.py` | Keep until R1, then remove |
| `extensions/cache.py` | Dead facade | None | Delete in R1 |
| `extensions/maintenance.py` | Legacy facade | `tests/test_security_extensions.py` | Keep until R2 |
| `extensions/signing.py` | Legacy facade | `tests/test_security_extensions.py` | Keep until R2 |
| `extensions/i18n.py` | Unused facade | None | Delete in R1 or wire it |

## 7. Configuration Sprawl

`AppConfig` (config.py, 307 LOC) contains 35+ fields spanning:
- Application metadata (app_name, project_name, host, port, workers, debug)
- Language/locale (language)
- Database toggles (enabled_databases, mysql_enabled, redis_enabled, etc.)
- Auth config (enable_auth, auth_secret, auth_app, auth_expire, auth_white_ip_list)
- Signing config (enable_signing, signing_secret)
- i18n toggle (enable_i18n)
- Cache toggle (enable_response_cache)
- CORS config (6 fields)
- Logging config (7 fields)
- Crypto config (crypt_response_enabled, crypt_response_secret, crypt_params_secret)
- Database connection dicts (mysql, redis, mongo)

This monolithic config should be split into capability-scoped config objects.

## 8. create_app() Assembly

`create_app()` in `app.py` performs 13 steps:
1. Load config
2. Create Sanic instance
3. Set app config
4. Setup logging
5. Register CORS + request-id middleware
6. Install context middleware (execution, routing, in-flight, cleanup)
7. Install auth middleware (lazy import)
8. Install tenant middleware (lazy import)
9. Register blueprints
10. Register lifecycle (startup/teardown listeners, health routes)
11. Register static file routes
12. Compile route policies (deadline wrapping)
13. Register exception handlers

This is pure composition — correct for `app.py`, but steps 5-8 represent 4 different middleware registration mechanisms that should converge.

## 9. Technical Debt Priority

| Priority | Issue | Risk | Phase |
|---|---|---|---|
| P0 | `sanic_adapter.py` is a god module (360+ LOC, 20+ functions) | Hard to maintain, test, or extend | C2-R2 |
| P0 | `system -> auth/tenant` coupling in `sanic_adapter.py` (binding reset) | Violates layer boundaries | C2-R3 |
| P1 | `exception <-> system` circular dependency | Import fragility | C2-R2 |
| P1 | Legacy auth (`middleware/auth.py`) shadows new auth system | Confusion, dual auth paths | C2-R1 |
| P1 | `RoutePolicy` dual model (old 4-field vs new 7-field) | `signing_required` lost in migration | C2-R4 |
| P2 | `_deep_freeze` triplication | Maintenance burden | C2-R2 |
| P2 | Binding pattern repetition (4 copies) | Maintenance burden | C2-R2 |
| P2 | Monolithic `AppConfig` (35+ fields) | Config sprawl | C2-R5 |
| P2 | `model/` depends on global proxies (`lingshu.db`, `lingshu.request`) | Untestable without request context | C2-R6 |
| P3 | Dead code (`middleware/cache.py`, unused utils) | Noise, confusion | C2-R1 |
| P3 | Error codes scattered across middleware files | No central registry | C2-R5 |

## 10. Confirmed Facts vs Inferences

### Confirmed (verified by reading code)
- No file directly `import sanic` — all Sanic integration is duck-typed via runtime parameters.
- `i18n.setup_i18n()` is never called by `create_app()`.
- `middleware/cache.py` `Cache` class has zero instantiation sites outside its own file.
- `middleware/utils.json_response` has a different signature from `response.json_response`.
- `RoutePolicyDefinition` does not have a `signing_required` field.
- `system.auth` never imports `system.auth.tenant`.
- `cli/project.py` enforces the "no `lingshu.system` imports in business code" rule via AST.

### Inferences (not verified by runtime testing)
- `middleware/auth.py` is likely not wired into the active request pipeline (based on import analysis showing it's only re-exported, not installed as middleware).
- `extensions/i18n.py` may have been intended for lifecycle-based setup but was never connected.
- The `signing_required` field on `RoutePolicy` may be consumed somewhere in `system.policy` that the AST analysis missed (possible runtime getattr access).

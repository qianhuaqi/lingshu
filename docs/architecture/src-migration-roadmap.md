# src Migration Roadmap

Phase: C2-R0
Issue: #19
Baseline: 446 passed, 1 skipped, 0 failed

## Migration Principles

1. **Small steps:** Each phase is one PR, one branch, independently reviewable and revertable.
2. **Public API stability:** All public facades (`lingshu.auth`, `lingshu.tenant`,
   `from lingshu import request`) remain unchanged throughout migration.
3. **Test gate:** Every phase must pass the full test suite (446+ passed) before merge.
4. **No big-bang:** No phase moves more than one subsystem. No phase deletes code that
   has active consumers (legacy code goes to `compat/` first, is deleted after C3).
5. **Dependency narrowing:** Each phase should reduce, not increase, circular dependencies.

## Phase Dependency Graph

```
R1 (auth dedup + dead code)
├── R2 (sanic_adapter split + cleanup registry)
│   ├── R3 (tenant -> contrib)
│   └── R4 (RoutePolicy unification)
├── R5 (config modularization)
└── R6 (model layer decoupling)
```

R2 depends on R1 (auth must be deduplicated before adapter split).
R3 depends on R2 (cleanup registry must exist before tenant can be decoupled).
R4 depends on R2 (policy compiler needs to be in adapters first).
R5 and R6 can proceed in parallel after R1.

---

## C2-R1: Auth Deduplication + Dead Code Removal

**Branch:** `codex/phase-c2-r1-auth-dedup`
**PR title:** `refactor(c2-r1): consolidate auth entry points and remove dead code`

### Scope
- Move `middleware/auth.py` to `compat/auth.py` (keep `Auth`/`token_required` as shims).
- Update `extensions/auth.py` to re-export from `compat/auth.py`.
- Delete `middleware/__init__.py` (`init_app` stub — zero callers).
- Delete `middleware/cache.py` + `extensions/cache.py` (dead code — zero consumers).
- Delete unused functions in `middleware/utils.py` (`filter_zjh`, `get_nonce_str`,
  `get_server_ip`, `get_ip`, `exists_path`).
- Keep `middleware/utils.py` legacy `json_response` but mark it with a deprecation comment.

### Forbidden
- No changes to `system/auth/*`.
- No changes to `system/auth/tenant/*`.
- No changes to `system/sanic_adapter.py`.
- No changes to any test other than updating import paths.

### Public API compat
- `from lingshu.middleware.auth import Auth` still works (re-export from compat).
- `from lingshu.extensions.auth import Auth` still works.
- `from lingshu.extensions.cache import Cache` raises ImportError (dead code removed).
  - Test `test_security_extensions.py` updated to remove cache callable check.

### Test contract
- `tests/test_c2_auth.py`: 111 passed (no regression).
- `tests/test_c2_tenant.py`: 127 passed (no regression).
- `tests/test_security_extensions.py`: Updated to remove Cache assertion.
- Full suite: ≥446 passed (adjusted for removed test assertions).

### Rollback
- Pure code movement + deletion. Revert the PR to restore.

---

## C2-R2: Sanic Adapter Split + Cleanup Hook Registry

**Branch:** `codex/phase-c2-r2-adapter-split`
**PR title:** `refactor(c2-r2): split sanic_adapter and introduce cleanup hook registry`

### Scope
- Split `system/sanic_adapter.py` (360+ LOC) into:
  - `adapters/sanic/context_middleware.py` — `install_context_middleware` + request lifecycle
  - `adapters/sanic/resource_registry.py` — `set_resource`/`get_resource`/`get_app_config`/etc.
  - `adapters/sanic/finalize.py` — `finalize_request_context` + cleanup hook registry
  - `adapters/sanic/routing.py` — `_route_policy_for_request` + `_request_route_name`
- Introduce `register_request_cleanup(hook)` in `adapters/sanic/finalize.py`.
- Refactor `_reset_principal_binding` and `_reset_tenant_binding` into registered hooks
  (auth and tenant modules register their own cleanup).
- Extract `_deep_freeze` into `core/types.py`.
- Extract `Binding` base protocol into `core/types.py`.
- Move `system/registry.py` and `system/resources.py` (3-line re-export shims) into
  the new `adapters/sanic/resource_registry.py`.

### Forbidden
- No changes to middleware installation order.
- No changes to `system/policy.py` compilation logic.
- No changes to any public API.
- No changes to `system/tasks.py`.

### Public API compat
- `from lingshu.system.sanic_adapter import *` still works (compat re-exports from
  new locations).
- `from lingshu.system import sanic_adapter` still works.

### Test contract
- All existing tests pass unchanged.
- New tests for cleanup hook registry: verify auth/tenant cleanup hooks are called
  on normal/exception/timeout/cancel paths.
- Full suite: ≥446 passed.

### Rollback
- Revert the PR. The split is mechanical — no logic changes.

---

## C2-R3: Tenant Module Relocation

**Branch:** `codex/phase-c2-r3-tenant-contrib`
**PR title:** `refactor(c2-r3): move tenant from auth internal to contrib module`

### Scope
- Move `system/auth/tenant/` directory to `contrib/tenant/`.
- Update all import paths:
  - `system/auth/tenant/context.py` → `contrib/tenant/context.py`
  - `system/auth/tenant/result.py` → `contrib/tenant/result.py`
  - etc.
- Update `lingshu.tenant` facade to import from new location.
- Update `adapters/sanic/finalize.py` to use the registered cleanup hook
  (no longer hardcodes `lingshu_tenant_binding`).
- Update test imports (tests import from `lingshu.tenant`, not `lingshu.system.auth.tenant`).

### Forbidden
- No logic changes to any tenant resolver, middleware, or binding.
- No changes to `system/auth/*` (auth stays as-is, just loses the tenant/ subdirectory).
- No changes to public API (`lingshu.tenant.*` unchanged).

### Public API compat
- `from lingshu.tenant import *` — unchanged.
- `from lingshu.system.auth.tenant import *` — compat re-export shims added
  at old location for one release cycle.

### Test contract
- `tests/test_c2_tenant.py`: 127 passed (only import paths change, if any).
- Full suite: ≥446 passed.

### Rollback
- Move directory back. No logic changes to revert.

---

## C2-R4: RoutePolicy Unification

**Branch:** `codex/phase-c2-r4-policy-unification`
**PR title:** `refactor(c2-r4): unify RoutePolicy public and internal definitions`

### Scope
- Add `signing_required` field to `RoutePolicyDefinition` (currently missing —
  exists only on legacy `RoutePolicy`).
- Make `RoutePolicy` (in `router.py`) a thin alias/subclass of `RoutePolicyDefinition`.
- Remove `from_legacy()` conversion path (both definitions become the same type).
- Update `RoutePolicyCompiler._normalize_definition()` to handle unified type directly.

### Forbidden
- No changes to policy compilation/wrapping logic.
- No changes to deadline/timeout behavior.
- No changes to auth/tenant middleware.

### Public API compat
- `RoutePolicy(auth_required=True, signing_required=False, tenant_required=False)` —
  unchanged signature.
- `RoutePolicyDefinition(...)` — gains `signing_required` field (additive).

### Test contract
- `tests/test_c2_auth.py`: 111 passed.
- `tests/test_c2_tenant.py`: 127 passed.
- New tests for `RoutePolicyDefinition.signing_required` compilation.
- Full suite: ≥446 passed.

### Rollback
- Revert the PR. The unification is additive.

---

## C2-R5: Configuration Modularization

**Branch:** `codex/phase-c2-r5-config-modular`
**PR title:** `refactor(c2-r5): split AppConfig into capability-scoped config objects`

### Scope
- Split `AppConfig` (35+ fields) into:
  - `AppMetaConfig` — app_name, project_name, host, port, workers, debug, language
  - `AuthConfig` — enable_auth, auth_secret, auth_app, auth_expire, auth_white_ip_list
  - `SigningConfig` — enable_signing, signing_secret
  - `DatabaseConfig` — enabled_databases, mysql_enabled, etc. + connection dicts
  - `CORSConfig` — cors_enabled, cors_origins, cors_allow_methods, etc.
  - `LoggingConfig` — log_to_file, log_level, log_path, etc.
  - `CryptoConfig` — crypt_response_enabled, crypt_response_secret, crypt_params_secret
- `AppConfig` becomes a frozen container holding these sub-configs.
- Backward compat: `app_config.auth_secret` delegates to `app_config.auth.secret`.

### Forbidden
- No changes to `.env` file format.
- No changes to environment variable names.
- No new dependencies.

### Test contract
- All existing tests pass.
- New tests for sub-config access patterns.
- Full suite: ≥446 passed.

### Rollback
- Revert. The split is structural, not behavioral.

---

## C2-R6: Model Layer Decoupling

**Branch:** `codex/phase-c2-r6-model-decouple`
**PR title:** `refactor(c2-r6): decouple model layer from global request proxy`

### Scope
- Refactor `Model` (model/model.py) to accept `db` and `redis` as parameters
  instead of importing `lingshu.db` global.
- Refactor `BusinessModel` (model/business.py) to accept `request` as parameter
  instead of importing `lingshu.request` global.
- Keep backward-compat: if `db`/`redis`/`request` not passed, fall back to globals
  with a deprecation warning.
- Move `model/` directory to `data/model/`.
- Move `database/` directory to `data/database/`.

### Forbidden
- No changes to SQL generation logic.
- No changes to cache behavior.
- No changes to scaffold templates (they generate code using the old import paths).

### Test contract
- All existing tests pass.
- New tests for dependency-injected model access.
- Full suite: ≥446 passed.

### Rollback
- Revert. The changes are additive (parameters have defaults).

---

## Compatibility Period

- **C2-R1 through C2-R6:** All legacy import paths work via compat shims.
- **After C3 acceptance:** Compat shims are removed in a cleanup PR.
- **User migration guide:** Documented in scaffold README, updated per phase.

## Test Baseline

| Checkpoint | Minimum |
|---|---|
| After each R phase | 446 passed, 1 skipped, 0 failed |
| After R1 (dead code removed) | 446 - (removed assertions) passed |
| After all R phases | ≥446 passed |

## C2.2B Resume Condition

C2.2B (and later C3) may begin only after:
1. C2-R1 through C2-R4 are merged and accepted.
2. C2-R5 and C2-R6 may proceed in parallel with C2.2B if they don't touch auth/tenant/middleware.
3. The `exception <-> system` circular dependency is resolved (R2).
4. `sanic_adapter.py` is split (R2).
5. Tenant module is relocated to `contrib/tenant/` (R3).

These conditions ensure C2.2B builds on a clean layer structure.

# LingShu V3 Testing and Stability Plan

Project: LingShu Framework
Owner: 多多
Planner / PM: 小顾
Status: active V3 plan

## 0. V3 goal

V3 must make V1 and V2 reliable enough for internal project use.

V3 does not primarily add new feature modules. V3 hardens all V1 capabilities and all V2 generated projects through tests, integration checks, regression checks, and acceptance demos.

## 1. V3 delivery rule

A V3 task is progress only if it adds or improves:

- unit test coverage;
- integration test coverage;
- generated project test coverage;
- end-to-end admin acceptance flow;
- cross-platform path/command stability;
- regression protection for previously fixed failures;
- clear validation commands.

## 2. Test layers

| Layer | Purpose |
| --- | --- |
| Unit tests | Prove individual modules work. |
| Integration tests | Prove modules work together. |
| Example tests | Prove examples run. |
| CLI tests | Prove commands generate and inspect projects. |
| Generated project tests | Prove generated projects can run their own tests. |
| End-to-end tests | Prove admin starter works as a real flow. |
| Regression tests | Prevent old failures from returning. |

## 3. Database tests

| Area | Required coverage |
| --- | --- |
| `lingshu.db` | DB factories, URL parser, config, error hierarchy. |
| SQLite | file DB, memory DB, connect, close, CRUD. |
| MySQL | adapter boundary, pool behavior, execute/query, transaction. |
| PostgreSQL | adapter boundary, URL/config, optional driver error. |
| Transaction | commit, rollback, exception cleanup, nested behavior decision. |
| Connection pool | acquire/release/close/error cleanup. |
| Safety | parameter binding and SQL injection strings. |
| Schema inspection | table/column/index inspection. |
| Batch execute | bulk insert/update. |
| Seed data | seed runner and idempotency. |
| Errors | safe message, code, internal cause not exposed. |

## 4. Query builder tests

| Area | Required coverage |
| --- | --- |
| select | field list and `*`. |
| where | all supported operators. |
| order_by | asc/desc. |
| limit/offset | pagination SQL. |
| insert | dict to parameterized insert. |
| update | dict update with explicit where. |
| delete | explicit where required. |
| params | user input is bound, not interpolated. |
| SQLite execution | generated query works on SQLite. |

## 5. ORM tests

| Area | Required coverage |
| --- | --- |
| Model declaration | table name and fields. |
| Field types | integer, text, boolean, datetime. |
| Primary key | create and read by primary key. |
| save | insert and update. |
| get | returns model or None. |
| delete | removes record. |
| to_dict | stable JSON-friendly dict. |
| validation | invalid field values rejected or converted as designed. |

## 6. Migration tests

| Area | Required coverage |
| --- | --- |
| migration table | `_lingshu_migrations` created. |
| apply | pending migrations run in order. |
| status | applied and pending visible. |
| rollback | latest migration can downgrade. |
| idempotency | applied migration not re-run. |
| failure | failed migration stops safely. |
| seed | seed idempotent and testable. |

## 7. Redis tests

| Area | Required coverage |
| --- | --- |
| connection | missing dependency and fake backend. |
| key/value | get/set/delete/exists. |
| TTL | expiry and ttl reading. |
| Hash | hget/hset/hgetall/hdel. |
| List | lpush/rpush/lpop/rpop/llen. |
| Set | sadd/srem/smembers. |
| Counter | incr/decr. |
| Lock | acquire/release/ttl. |
| Pub/Sub | publish/subscribe boundary. |
| Stream | xadd/xread boundary. |
| Serialization | dict/list/scalar round trip. |
| Namespace | prefix isolation. |

## 8. MongoDB tests

| Area | Required coverage |
| --- | --- |
| connection | missing dependency and fake backend. |
| collection | collection object. |
| insert | insert_one/insert_many. |
| find | find_one/find. |
| projection | field projection. |
| sort | sorting. |
| limit/skip | pagination. |
| count | count docs. |
| update | update_one/update_many. |
| delete | delete_one/delete_many. |
| index | create/drop index. |
| aggregate | pipeline pass-through. |
| ObjectId | safe ID handling. |
| errors | stable error wrapping. |

## 9. Cache tests

| Area | Required coverage |
| --- | --- |
| MemoryCache | set/get/delete/exists/ttl. |
| RedisCache | fake or optional backend. |
| serializer | JSON round trip. |
| namespace | isolation. |
| app.cache | handler access. |
| lifecycle | startup/shutdown cleanup. |

## 10. Validation tests

| Area | Required coverage |
| --- | --- |
| path params | type conversion and invalid values. |
| query params | defaults, required, type conversion. |
| body | required fields, types, invalid JSON. |
| form | form field validation. |
| file | file validation. |
| error response | stable validation error body. |
| OpenAPI | validation metadata appears in docs. |

## 11. Response tests

| Area | Required coverage |
| --- | --- |
| JSON response | dict/list/model serialization. |
| success envelope | data/meta shape. |
| error envelope | code/message/details shape. |
| pagination | page/page_size/total/items. |
| file response | local file response. |
| redirect | status and location. |
| datetime/model | serialization edge cases. |

## 12. OpenAPI tests

| Area | Required coverage |
| --- | --- |
| `/openapi.json` | valid JSON and routes. |
| `/docs` | HTML returns. |
| metadata | summary/tags/description. |
| validation schema | request schema appears. |
| response schema | response schema appears. |
| auth markers | protected route marked. |
| permission markers | permission requirement marked. |

## 13. Upload and storage tests

| Area | Required coverage |
| --- | --- |
| multipart | valid file upload. |
| missing field | readable error. |
| size limit | oversized file rejected. |
| metadata | filename/content_type/size. |
| safe filename | traversal blocked. |
| local storage | save/delete/exists. |
| metadata | hash/size/type. |
| file response | stored file can be served or referenced. |

## 14. Auth, session, and RBAC tests

| Area | Required coverage |
| --- | --- |
| password | hash/verify. |
| login | success and failure. |
| token | create/verify/invalid/expired. |
| request.user | middleware populates user. |
| require_login | unauthenticated rejected; authenticated allowed. |
| session | signed cookie, session store, expiry. |
| roles | user-role mapping. |
| permissions | role-permission mapping. |
| require_permission | no permission rejected; permission allowed. |
| admin seed | seeded admin can login. |

## 15. Security tests

| Area | Required coverage |
| --- | --- |
| CORS | allowed/disallowed origin behavior. |
| security headers | configured headers present. |
| body size | oversized request rejected. |
| host allowlist | invalid host rejected when enabled. |
| trusted proxy | proxy headers only trusted when configured. |
| CSRF interface | cookie/session mode protection behavior. |
| rate-limit seam | local/fake limiter behavior. |
| redaction | tokens/passwords/secrets not leaked. |

## 16. Config and error tests

| Area | Required coverage |
| --- | --- |
| `.env` | file loading. |
| env override | environment wins. |
| URL parsing | DB/Redis/Mongo URLs. |
| APP_SECRET | required for auth/session. |
| typed config | int/bool/path/list conversions. |
| redaction | config logs hide secrets. |
| error codes | stable code per module. |
| safe message | no traceback/SQL/secrets in client output. |
| HTTP mapping | 401/403/422/500 mapping. |

## 17. Logging, audit, health, pagination, tasks tests

| Module | Required coverage |
| --- | --- |
| logging | request log, error log, trace ID, redaction. |
| audit | actor/action/resource/result, decorator, DB persistence seam. |
| health | `/health`, `/ready`, dependency status. |
| pagination | params, max page size, response helper. |
| tasks | background task, registry, retry boundary, shutdown cleanup. |

## 18. Testing helper tests

| Helper | Required coverage |
| --- | --- |
| test client | route request and response assertions. |
| JSON helper | POST JSON and parse response. |
| upload helper | multipart test request. |
| auth helper | token/login helper. |
| temp DB fixture | temp SQLite DB. |
| app factory helper | lifecycle-safe test app creation. |

## 19. CLI tests

| Command | Required coverage |
| --- | --- |
| `lingshu new` | files created, imports, tests pass. |
| `lingshu new-api` | files created, DB init, users tests pass. |
| `lingshu new-admin` | files created, DB init, auth/RBAC/upload/docs tests pass. |
| `lingshu run` | target import and safe failure. |
| `lingshu check` | success and failure diagnostics. |
| `lingshu routes` | route table output. |
| `lingshu db init` | migrations/seed applied idempotently. |
| `lingshu doctor` | environment diagnostics. |

## 20. Generated project tests

Fresh generated projects must run their own tests:

```powershell
lingshu new myapp
cd myapp
python -m pytest
```

```powershell
lingshu new-api myapi
cd myapi
lingshu db init
python -m pytest
```

```powershell
lingshu new-admin myadmin
cd myadmin
lingshu db init
python -m pytest
```

## 21. Admin end-to-end acceptance flow

Fresh admin project must pass:

```powershell
lingshu new-admin demo_admin
cd demo_admin
lingshu db init
lingshu check app:app
lingshu routes app:app
lingshu run app:app
```

Then verify:

| Request | Expected |
| --- | --- |
| `GET /health` | healthy JSON. |
| `GET /ready` | ready JSON with dependency status. |
| `GET /docs` | docs page. |
| `GET /openapi.json` | schema JSON. |
| `POST /login` | token or session. |
| `GET /me` without token | auth error. |
| `GET /me` with token | current user. |
| protected route without token | auth error. |
| permission route without permission | permission error. |
| permission route with permission | success. |
| upload route | saves file and returns metadata/path. |
| audit query | shows operation audit when enabled. |

## 22. Cross-platform stability

V3 must verify:

| Platform area | Requirement |
| --- | --- |
| Windows paths | generated projects and uploads use safe paths. |
| Linux paths | generated projects and uploads use safe paths. |
| PowerShell commands | documented commands work. |
| shell commands | documented commands work. |
| line endings | generated files are stable. |

## 23. V3 issue breakdown

| Issue | Main delivery |
| --- | --- |
| V3-01 | database/query/ORM/migration tests. |
| V3-02 | Redis/Mongo/cache tests. |
| V3-03 | validation/response/openapi tests. |
| V3-04 | upload/storage tests. |
| V3-05 | auth/session/RBAC tests. |
| V3-06 | security/config/errors tests. |
| V3-07 | logging/audit/health/pagination/tasks tests. |
| V3-08 | testing helper tests. |
| V3-09 | CLI command tests. |
| V3-10 | generated project tests. |
| V3-11 | admin end-to-end acceptance. |
| V3-12 | final regression and release readiness. |

## 24. Final validation

Repository validation:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy lingshu tests
.\.venv\Scripts\python.exe -m pytest
```

Generated project validation:

```powershell
lingshu new myapp
cd myapp
python -m pytest
```

```powershell
lingshu new-api myapi
cd myapi
lingshu db init
python -m pytest
```

```powershell
lingshu new-admin myadmin
cd myadmin
lingshu db init
lingshu check app:app
lingshu routes app:app
python -m pytest
```

V3 is complete only when repository tests, example tests, CLI tests, generated project tests, and admin end-to-end acceptance pass.
